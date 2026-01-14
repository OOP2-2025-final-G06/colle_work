from routes import db
from routes import user_manager

def get_salary() -> float:
    conn = db.get_conn()
    cur = conn.execute("SELECT value FROM configs WHERE key = 'salary_per_hour'")
    row = cur.fetchone()
    conn.close()
    return float(row["value"]) if row else 1000.0

def set_salary(value: float):
    conn = db.get_conn()
    conn.execute("INSERT OR REPLACE INTO configs (key, value) VALUES ('salary_per_hour', ?)", (str(value),))
    conn.commit()
    conn.close()

def get_wage_records():
    conn = db.get_conn()
    cur = conn.execute("SELECT * FROM wages ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def save_wage(username: str, shift_hour: float):
    salary_per_hour = get_salary()
    salary = shift_hour * salary_per_hour
    token = int(shift_hour * 5)

    conn = db.get_conn()
    conn.execute("""
        INSERT INTO wages (username, shift_hour, salary_per_hour, salary, token)
        VALUES (?, ?, ?, ?, ?)
    """, (username, shift_hour, salary_per_hour, salary, token))
    conn.commit()
    conn.close()

    # ユーザーにトークンを付与
    user_manager.add_token(username, token)

    return salary, token