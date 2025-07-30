import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, district TEXT, role TEXT)')
    print("Users table created successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, district TEXT)')
    print("Teams table created successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS quizzers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, team_id INTEGER, FOREIGN KEY(team_id) REFERENCES teams(id))')
    print("Quizzers table created successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS districts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
    print("Districts table created successfully")

    conn.close()

def populate_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    teams_data = [
        {'name': 'VTR', 'coach': 'Coach Melissa Hawthorne', 'quizzers': ['Aiden R.', 'Jasmine T.', 'Leo M.', 'Brooklyn S.', 'Carter D.']},
        {'name': 'KLP', 'coach': 'Coach Tony Delgado', 'quizzers': ['Mia L.', 'Nolan F.', 'Zoe W.', 'Elijah B.', 'Skylar J.']},
        {'name': 'ZQN', 'coach': 'Coach Rebecca Kim', 'quizzers': ['Grayson P.', 'Lily A.', 'Mateo V.', 'Ava N.', 'Dominic K.']},
        {'name': 'DRX', 'coach': 'Coach Jamal Rivers', 'quizzers': ['Chloe G.', 'Mason E.', 'Isabella Q.', 'Caleb Z.', 'Riley H.']},
        {'name': 'MJB', 'coach': 'Coach Sandra Lin', 'quizzers': ['Lucas T.', 'Harper Y.', 'Ethan J.', 'Aria S.', 'Owen C.']},
    ]

    for team_data in teams_data:
        cur.execute('INSERT INTO teams (name, district) VALUES (?, ?)', (team_data['name'], ''))
        team_id = cur.lastrowid

        cur.execute('INSERT INTO users (username, password, district, role) VALUES (?, ?, ?, ?)',
                     (team_data['coach'], 'password', '', 'Coach'))

        for quizzer_name in team_data['quizzers']:
            cur.execute('INSERT INTO quizzers (name, team_id) VALUES (?, ?)', (quizzer_name, team_id))

    conn.commit()
    conn.close()
    print("Database populated successfully")

if __name__ == '__main__':
    init_db()
    populate_db()
