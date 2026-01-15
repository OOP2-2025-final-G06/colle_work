import sqlite3
from datetime import datetime
from routes import user_manager
from routes import game_manager 


# 設定 (Constants)

TOKEN_PER_HOUR = 10
DB_PATH = "database.db"  


# データベース初期化

def init_wage_db():
    """時給保存用のテーブルを作成"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_wages (
                username TEXT PRIMARY KEY,
                salary INTEGER
            )
        """)

# ファイル読み込み時に初期化を実行
init_wage_db()


# 時給管理 (DB化)

def get_salary(username: str) -> int:
    """DBから時給を取得（なければデフォルト1000円）"""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT salary FROM user_wages WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            return row[0]
        else:
            return 1000

def set_salary(username: str, value: int):
    """DBに時給を保存"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO user_wages (username, salary)
            VALUES (?, ?)
        """, (username, value))



# ユーザー & token 管理


def get_user_token(username: str) -> int:
    return game_manager.get_user_token_from_db(username)




wage_records = []

def get_wage_records():
    return wage_records

def get_monthly_earnings(username: str) -> int:
    today = datetime.now()
    current_month = today.strftime("%Y-%m")
    total = 0
    for record in wage_records:
        if record["username"] == username and record["date"].startswith(current_month):
            total += record["salary"]
    return total

def get_yearly_earnings(username: str) -> int:
    today = datetime.now()
    current_year = today.strftime("%Y")
    total = 0
    for record in wage_records:
        if record["username"] == username and record["date"].startswith(current_year):
            total += record["salary"]
    return total

def get_monthly_forecast(username: str) -> int:
    hourly = get_salary(username)
    return hourly * 15 * 4

def get_yearly_forecast(username: str) -> int:
    hourly = get_salary(username)
    return hourly * 15 * 52



# 給料 & token 計算・保存


def save_wage(username: str, shift_hour: float, date_str: str = None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    salary_per_hour = get_salary(username) # ここでDBから時給を取得
    salary = int(shift_hour * salary_per_hour)
    token = int(shift_hour * TOKEN_PER_HOUR)

    # 履歴保存
    wage_records.append({
        "username": username,
        "date": date_str,
        "shift_hour": shift_hour,
        "salary_per_hour": salary_per_hour,
        "salary": salary,
        "token": token
    })

    # DBにトークン加算
    game_manager.add_user_token_to_db(username, token)

    return salary, token