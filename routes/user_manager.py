# routes/user_manager.py
import sqlite3

DB_NAME = "database.db"


def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            token INTEGER DEFAULT 0,
            salary INTEGER DEFAULT 1000
        )
    """)
    conn.commit()
    conn.close()


def get_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users


def register_user(username, password):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM users WHERE username=? AND password=?",
        (username, password)
    )
    result = c.fetchone()
    conn.close()
    return result is not None


def get_user_token(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT token FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def add_token(username, token):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET token = token + ? WHERE username=?",
        (token, username)
    )
    conn.commit()
    conn.close()


def set_salary(username, salary):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET salary=? WHERE username=?",
        (salary, username)
    )
    conn.commit()
    conn.close()


def get_salary(username):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT salary FROM users WHERE username=?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    return row[0] if row else 1000
