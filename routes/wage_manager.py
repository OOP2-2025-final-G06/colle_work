# routes/wage_manager.py
from datetime import datetime
from routes import user_manager
# ★ game_manager をインポートしてDBを操作できるようにする
from routes import game_manager 

# =========================
# 設定 (Constants)
# =========================

TOKEN_PER_HOUR = 10

# =========================
# 時給管理
# =========================

user_salaries = {
    "testuser": 1000
}

def get_salary(username: str) -> int:
    return user_salaries.get(username, 1000)

def set_salary(username: str, value: int):
    user_salaries[username] = value

# =========================
# ユーザー & token 管理
# =========================

# ★ ここを変更：メモリ上の辞書ではなく、DBから最新の値を取ってくる
def get_user_token(username: str) -> int:
    return game_manager.get_user_token_from_db(username)

# =========================
# 給料履歴管理
# =========================

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

# =========================
# 給料 & token 計算・保存
# =========================

def save_wage(username: str, shift_hour: float, date_str: str = None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    salary_per_hour = get_salary(username)
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

    # ★ ここを変更：DBに直接トークンを加算する
    game_manager.add_user_token_to_db(username, token)

    return salary, token