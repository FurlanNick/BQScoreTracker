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

if __name__ == '__main__':
    init_db()
