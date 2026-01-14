from routes import db
from typing import List, Dict

def get_users() -> List[str]:
    conn = db.get_conn()
    cur = conn.execute("SELECT username FROM users")
    users = [row["username"] for row in cur.fetchall()]
    conn.close()
    return users

def register_user(username: str, password: str) -> bool:
    conn = db.get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password, tokens) VALUES (?, ?, ?)",
            (username, password, 0)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    conn = db.get_conn()
    cur = conn.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return row["password"] == password

def add_token(username: str, token: int):
    conn = db.get_conn()
    conn.execute(
        "UPDATE users SET tokens = COALESCE(tokens,0) + ? WHERE username = ?",
        (token, username)
    )
    conn.commit()
    conn.close()

def get_user_token(username: str) -> int:
    conn = db.get_conn()
    cur = conn.execute("SELECT tokens FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return int(row["tokens"]) if row and row["tokens"] is not None else 0

def get_all_user_tokens() -> Dict[str, int]:
    conn = db.get_conn()
    cur = conn.execute("SELECT username, tokens FROM users")
    res = {row["username"]: int(row["tokens"] or 0) for row in cur.fetchall()}
    conn.close()
    return res


# === ここから追加 ===
def init_test_user():
    conn = db.get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password, tokens) VALUES (?, ?, ?)",
            ("testuser", "password", 0)
        )
        conn.commit()
    except Exception:
        # 既に存在する場合などは無視
        pass
    finally:
        conn.close()


# アプリ起動時などに一度だけ呼ぶ
init_test_user()
