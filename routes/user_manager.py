# routes/user_manager.py

# ユーザーデータとトークン管理（仮データベース）
users = {
    "testuser": "password"
}

user_tokens = {
    "testuser": 0
}

wage_records = []

def get_users():
    """全ユーザー情報を返す"""
    return users

def register_user(username, password):
    """
    新規登録処理
    登録成功なら True, 重複していて失敗なら False を返す
    """
    if username in users:
        return False
    users[username] = password
    
    # トークン初期化
    if username not in user_tokens:
        user_tokens[username] = 0
    return True

def verify_user(username, password):
    """
    ログイン認証処理
    成功なら True, 失敗なら False を返す
    """
    if username in users and users[username] == password:
        # トークン初期化（念の為）
        if username not in user_tokens:
            user_tokens[username] = 0
        return True
    return False

def save_wage(username, shift_hour, salary_per_hour):
    """給与計算とトークン保存を行い、結果を返す"""
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

    return salary, token