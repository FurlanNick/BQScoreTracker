from flask import Flask, render_template, request, redirect, url_for, session
import json

import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # This should be a random, secret value

def get_db_connection():
    conn = sqlite3.connect('../database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.app_context():
        db = conn
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.execute('INSERT INTO users (username, password, district, role) VALUES (?, ?, ?, ?)',
                     ('Admin', 'Admin', 'All', 'Admin'))

        teams_data = [
            {'name': 'VTR', 'coach': 'Coach Melissa Hawthorne', 'quizzers': ['Aiden R.', 'Jasmine T.', 'Leo M.', 'Brooklyn S.', 'Carter D.']},
            {'name': 'KLP', 'coach': 'Coach Tony Delgado', 'quizzers': ['Mia L.', 'Nolan F.', 'Zoe W.', 'Elijah B.', 'Skylar J.']},
            {'name': 'ZQN', 'coach': 'Coach Rebecca Kim', 'quizzers': ['Grayson P.', 'Lily A.', 'Mateo V.', 'Ava N.', 'Dominic K.']},
            {'name': 'DRX', 'coach': 'Coach Jamal Rivers', 'quizzers': ['Chloe G.', 'Mason E.', 'Isabella Q.', 'Caleb Z.', 'Riley H.']},
            {'name': 'MJB', 'coach': 'Coach Sandra Lin', 'quizzers': ['Lucas T.', 'Harper Y.', 'Ethan J.', 'Aria S.', 'Owen C.']},
        ]

        for team_data in teams_data:
            cur = db.cursor()
            cur.execute('INSERT INTO teams (name, district) VALUES (?, ?)', (team_data['name'], ''))
            team_id = cur.lastrowid

            db.execute('INSERT INTO users (username, password, district, role) VALUES (?, ?, ?, ?)',
                         (team_data['coach'], 'password', '', 'Coach'))

            for quizzer_name in team_data['quizzers']:
                db.execute('INSERT INTO quizzers (name, team_id) VALUES (?, ?)', (quizzer_name, team_id))

        db.commit()

# In-memory quiz database
quizzes = {}

from functools import wraps

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))

            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
            conn.close()

            if user['role'] != required_role and user['role'] != 'Admin':
                return redirect(url_for('competition'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def calculate_team_standings(quizzes):
    team_scores = {}
    for quiz_name, quiz_scores in quizzes.items():
        # This is a placeholder for the actual scoring logic
        for team_name, score in quiz_scores.items():
            if team_name not in team_scores:
                team_scores[team_name] = 0
            team_scores[team_name] += score

    standings = [{'name': team_name, 'score': score} for team_name, score in team_scores.items()]
    standings.sort(key=lambda x: x['score'], reverse=True)
    return standings

def calculate_quizzer_standings(quizzes):
    quizzer_scores = {}
    for quiz_name, quiz_data in quizzes.items():
        for team_index in range(1, 4):
            for i in range(1, 6):
                quizzer_name = quiz_data.get(f'quizzer_{team_index}_{i}')
                if quizzer_name:
                    if quizzer_name not in quizzer_scores:
                        quizzer_scores[quizzer_name] = {'score': 0, 'correct': 0, 'errors': 0}

                    for j in range(1, 27):
                        score = quiz_data.get(f'score_{team_index}_{i}_{j}')
                        if score == 'C':
                            quizzer_scores[quizzer_name]['score'] += 20
                            quizzer_scores[quizzer_name]['correct'] += 1
                        elif score == 'E':
                            quizzer_scores[quizzer_name]['errors'] += 1

    for quizzer_name, data in quizzer_scores.items():
        if data['correct'] >= 4 and data['errors'] == 0:
            data['score'] += 10

        if data['errors'] > 1:
            data['score'] -= (data['errors'] -1) * 10

    standings = [{'name': name, 'score': data['score']} for name, data in quizzer_scores.items()]
    standings.sort(key=lambda x: x['score'], reverse=True)
    return standings

def parse_quiz_template():
    with open('../template.json', 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and user['password'] == password:
            session['username'] = user['username']
            return redirect(url_for('competition'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/competition')
def competition():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
    conn.close()

    return render_template('competition.html', district=user['district'])

@app.route('/standings')
def standings():
    team_standings = calculate_team_standings(quizzes)
    quizzer_standings = calculate_quizzer_standings(quizzes)
    return render_template('standings.html', team_standings=team_standings, quizzer_standings=quizzer_standings)

@app.route('/quiz-meet')
def quiz_meet():
    return render_template('quiz-meet.html')

@app.route('/quiz-meet/<int:meet_number>')
def rooms(meet_number):
    return render_template('rooms.html', meet_number=meet_number)

@app.route('/quiz-meet/<int:meet_number>/room/<int:room_number>')
def quiz_list(meet_number, room_number):
    return render_template('quiz-list.html', meet_number=meet_number, room_number=room_number)

@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    conn = get_db_connection()
    teams_from_db = conn.execute('SELECT * FROM teams').fetchall()
    teams = [dict(row) for row in teams_from_db]
    users_from_db = conn.execute('SELECT * FROM users').fetchall()
    users = [dict(row) for row in users_from_db]

    scoresheet_data = conn.execute('SELECT data FROM scoresheets WHERE quiz_name = ?', (quiz_name,)).fetchone()
    conn.close()

    if scoresheet_data:
        scoresheet_data = json.loads(scoresheet_data['data'])

    return render_template('scoresheet.html', quiz_name=quiz_name, users=users, teams=teams, scoresheet_data=scoresheet_data)

@app.route('/accounts')
@role_required('Admin')
def accounts():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    districts = conn.execute('SELECT * FROM districts').fetchall()
    conn.close()
    return render_template('accounts.html', users=users, districts=districts)

@app.route('/add_user', methods=['POST'])
@role_required('Admin')
def add_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    district = request.form['district']

    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password, district, role) VALUES (?, ?, ?, ?)',
                 (username, password, district, role))
    conn.commit()
    conn.close()

    return redirect(url_for('accounts'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        district = request.form['district']

        conn.execute('UPDATE users SET username = ?, password = ?, role = ?, district = ? WHERE id = ?',
                     (username, password, role, district, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('accounts'))

    districts = conn.execute('SELECT * FROM districts').fetchall()
    conn.close()
    return render_template('edit_user.html', user=user, districts=districts)

@app.route('/delete_user/<int:user_id>')
@role_required('Admin')
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('accounts'))

@app.route('/edit_district/<int:district_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_district(district_id):
    conn = get_db_connection()
    district = conn.execute('SELECT * FROM districts WHERE id = ?', (district_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']

        conn.execute('UPDATE districts SET name = ? WHERE id = ?',
                     (name, district_id))
        conn.commit()
        conn.close()
        return redirect(url_for('accounts'))

    conn.close()
    return render_template('edit_district.html', district=district)

@app.route('/delete_district/<int:district_id>')
@role_required('Admin')
def delete_district(district_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM districts WHERE id = ?', (district_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('accounts'))

@app.route('/add_district', methods=['POST'])
@role_required('Admin')
def add_district():
    new_district = request.form['new_district']

    conn = get_db_connection()
    conn.execute('INSERT INTO districts (name) VALUES (?)', (new_district,))
    conn.commit()
    conn.close()

    return redirect(url_for('accounts'))

@app.route('/edit_quiz/<quiz_name>', methods=['POST'])
def edit_quiz(quiz_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    data = json.dumps(request.form)

    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO scoresheets (quiz_name, data) VALUES (?, ?)', (quiz_name, data))
    conn.commit()
    conn.close()

    return redirect(url_for('quiz', quiz_name=quiz_name))

@app.route('/create_team', methods=['GET', 'POST'])
def create_team():
    if request.method == 'POST':
        team_name = request.form['team_name']
        coaches = request.form.getlist('coaches')
        quizzers = request.form.getlist('quizzers')

        print(f"Adding team: {team_name}, Coaches: {coaches}, Quizzers: {quizzers}")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO teams (name, district, coach) VALUES (?, ?, ?)', (team_name, '', coaches[0]))
        team_id = cur.lastrowid

        for quizzer_name in quizzers:
            conn.execute('INSERT INTO quizzers (name, team_id) VALUES (?, ?)', (quizzer_name, team_id))

        conn.commit()
        conn.close()

        return redirect(url_for('competition'))

    return render_template('create_team.html')

@app.route('/get_quizzers/<team_name>')
def get_quizzers(team_name):
    conn = get_db_connection()
    team = conn.execute('SELECT * FROM teams WHERE name = ?', (team_name,)).fetchone()
    if team:
        quizzers = conn.execute('SELECT * FROM quizzers WHERE team_id = ?', (team['id'],)).fetchall()
    else:
        quizzers = []
    conn.close()
    print(quizzers)
    return json.dumps([dict(row) for row in quizzers])

@app.route('/team_info')
def team_info():
    conn = get_db_connection()
    teams_from_db = conn.execute('SELECT * FROM teams ORDER BY name').fetchall()
    teams = []
    for team in teams_from_db:
        team_dict = dict(team)
        quizzers = conn.execute('SELECT * FROM quizzers WHERE team_id = ?', (team['id'],)).fetchall()
        team_dict['quizzers'] = [quizzer['name'] for quizzer in quizzers]

        team_dict['coaches'] = [team['coach']]

        teams.append(team_dict)

    conn.close()
    return render_template('team_info.html', teams=teams)

@app.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_team(team_id):
    conn = get_db_connection()

    if request.method == 'POST':
        team_name = request.form['team_name']
        coaches = request.form.getlist('coaches')
        quizzers = request.form.getlist('quizzers')

        conn.execute('UPDATE teams SET name = ? WHERE id = ?', (team_name, team_id))

        conn.execute('DELETE FROM quizzers WHERE team_id = ?', (team_id,))
        for quizzer_name in quizzers:
            conn.execute('INSERT INTO quizzers (name, team_id) VALUES (?, ?)', (quizzer_name, team_id))

        conn.commit()
        conn.close()
        return redirect(url_for('team_info'))

    team_from_db = conn.execute('SELECT * FROM teams WHERE id = ?', (team_id,)).fetchone()
    team = dict(team_from_db)
    quizzers_from_db = conn.execute('SELECT * FROM quizzers WHERE team_id = ?', (team_id,)).fetchall()
    team['quizzers'] = [quizzer['name'] for quizzer in quizzers_from_db]
    team['coaches'] = [] # Placeholder

    conn.close()
    return render_template('edit_team.html', team=team)

@app.route('/delete_team/<int:team_id>', methods=['POST'])
@role_required('Admin')
def delete_team(team_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM teams WHERE id = ?', (team_id,))
    conn.execute('DELETE FROM quizzers WHERE team_id = ?', (team_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('team_info'))

@app.route('/view_db')
def view_db():
    conn = get_db_connection()
    teams = conn.execute('SELECT * FROM teams').fetchall()
    quizzers = conn.execute('SELECT * FROM quizzers').fetchall()
    conn.close()
    return json.dumps({'teams': [dict(row) for row in teams], 'quizzers': [dict(row) for row in quizzers]})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8090)
