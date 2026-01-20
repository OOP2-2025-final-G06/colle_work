# routes/user_manager.py
import sqlite3
from routes import game_manager  # ゲームDBからトークンを取得

DB_PATH = "database.db"

def init_db():
    """ユーザー管理用テーブルを作成（パスワードのみ）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------
# ユーザー管理
# -------------------------
def register_user(username, password):
    """新規登録"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """ログイン認証"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def get_all_users():
    """
    全ユーザーとトークンを返す {username: token}
    トークンはゲームDBから取得
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()

    # ゲームDBからトークン取得
    user_tokens = {u: game_manager.get_user_token_from_db(u) for u in users}
    return user_tokens

def get_user_token(username):
    """特定ユーザーのトークン取得（ゲームDB参照）"""
    return game_manager.get_user_token_from_db(username)
