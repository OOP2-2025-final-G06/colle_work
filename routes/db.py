import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent.parent / "database.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ユーザー
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        tokens INTEGER DEFAULT 0
    )
    """)

    # シフト（shift_manager も同テーブルを作るが二重作成しても OK）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        start_h TEXT,
        start_m TEXT,
        end_h TEXT,
        end_m TEXT,
        shift_hour REAL,
        UNIQUE(username, date)
    )
    """)

    # 給料履歴
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        shift_hour REAL,
        salary_per_hour REAL,
        salary REAL,
        token INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 設定（時給など）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS configs (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # デフォルト時給を入れておく
    cur.execute("INSERT OR IGNORE INTO configs (key, value) VALUES ('salary_per_hour', '1000')")

    conn.commit()
    conn.close()