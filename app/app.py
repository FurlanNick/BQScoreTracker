from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # This should be a random, secret value

# In-memory user database
users = {
    'Admin': {'password': 'Admin', 'district': 'All'}
}

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
    return render_template('standings.html')

@app.route('/quiz-meet')
def quiz_meet():
    return render_template('quiz-meet.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/accounts')
def accounts():
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    return render_template('accounts.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    district = request.form['district']

    if username not in users:
        users[username] = {'password': password, 'district': district}

    return redirect(url_for('accounts'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)
