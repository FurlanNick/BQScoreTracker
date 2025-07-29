from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # This should be a random, secret value

# In-memory user database
users = {
    'Admin': {'password': 'Admin', 'district': 'All', 'role': 'Admin'}
}

districts = [
    "Eastern Canadian District",
    "Central Canadian District",
    "Canadian Midwest District",
    "Western Canadian District",
    "Great Lakes District",
    "Western Great Lakes District",
    "Central District",
    "Ohio Valley District"
]

# In-memory team database
teams = {}

# In-memory quiz database
quizzes = {}

from functools import wraps

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))

            user_role = users[session['username']]['role']
            if user_role != required_role and user_role != 'Admin':
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
    # This is a placeholder for the actual scoring logic
    return []

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
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('competition'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/competition')
def competition():
    if 'username' not in session:
        return redirect(url_for('login'))

    district = users[session['username']]['district']
    return render_template('competition.html', district=district)

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
    return render_template('new_quiz_template.html', quiz_name=quiz_name, users=users, teams=teams)

@app.route('/accounts')
@role_required('Admin')
def accounts():
    return render_template('accounts.html', users=users, districts=districts)

@app.route('/add_user', methods=['POST'])
@role_required('Admin')
def add_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    district = request.form['district']

    if username not in users:
        users[username] = {'password': password, 'district': district, 'role': role}

    return redirect(url_for('accounts'))

@app.route('/add_district', methods=['POST'])
@role_required('Admin')
def add_district():
    new_district = request.form['new_district']
    if new_district not in districts:
        districts.append(new_district)

    return redirect(url_for('accounts'))

@app.route('/edit_quiz/<quiz_name>', methods=['POST'])
def edit_quiz(quiz_name):
    if 'username' not in session or users[session['username']]['role'] not in ['Admin', 'District', 'Official']:
        return redirect(url_for('login'))

    score = request.form['score']
    print(f"Quiz {quiz_name} score updated to: {score}")

    return redirect(url_for('quiz', quiz_name=quiz_name))

@app.route('/create_team', methods=['GET', 'POST'])
def create_team():
    if request.method == 'POST':
        team_name = request.form['team_name']
        coaches = request.form.getlist('coaches')
        quizzers = request.form.getlist('quizzers')

        if team_name not in teams:
            teams[team_name] = {'coaches': coaches, 'quizzers': quizzers}

        return redirect(url_for('competition'))

    return render_template('create_team.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
