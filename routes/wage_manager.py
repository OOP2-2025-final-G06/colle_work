# wage_manager.py
from routes import user_manager # ユーザーのトークン管理用にインポート

# =========================
# 時給管理
# =========================

# 時給（初期値）
_salary_per_hour = 1000


def get_salary():
    return _salary_per_hour


def set_salary(value: int):
    global _salary_per_hour
    _salary_per_hour = value


# =========================
# ユーザー & token 管理
# =========================

# 仮のユーザ情報（app.py 側と揃える前提）
users = {
    "testuser": "password"
}

# ユーザーごとの token 管理
user_tokens = {
    "testuser": 0
}


def get_user_token(username: str) -> int:
    return user_tokens.get(username, 0)


# =========================
# 給料履歴管理
# =========================

# 給料・token保存用（履歴）
wage_records = []


def get_wage_records():
    return wage_records


# =========================
# 給料 & token 計算・保存
# =========================

def save_wage(username: str, shift_hour: float):
    """
    シフト時間から給料とtokenを計算し保存する
    """
    salary_per_hour = get_salary()
    salary = shift_hour * salary_per_hour
    token = shift_hour * 5
    # 履歴保存
    wage_records.append({
        "username": username,
        "shift_hour": shift_hour,
        "salary_per_hour": salary_per_hour,
        "salary": salary,
        "token": token
    })
    # tokenをユーザーごとに加算
    if username not in user_tokens:
        user_tokens[username] = 0
    user_tokens[username] += token
    # tokenは user_manager に渡す
    user_manager.add_token(username, token)

    return salary, token