from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # This is where the login logic will go.
        # For now, we'll just redirect to the competition page.
        return redirect(url_for('competition'))
    return render_template('login.html')

@app.route('/competition')
def competition():
    return render_template('competition.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
