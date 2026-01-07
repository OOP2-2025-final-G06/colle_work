from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# 仮のユーザ情報
users = {"testuser": "password"}

# ユーザーごとの token 管理
user_tokens = {
    "testuser": 0
}

# 給料・token保存用（履歴）
wage_records = []

# 給料 & token 計算・保存
def save_wage(username, shift_hour, salary_per_hour):
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


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["username"] = username  # ★ ログインユーザー保持

            # token初期化（初ログイン時）
            if username not in user_tokens:
                user_tokens[username] = 0

            return redirect(url_for("top"))
        else:
            return render_template("login.html", error="ユーザ名かパスワードが間違っています")

    return render_template("login.html")

@app.route("/top")
def top():
    return render_template("top.html")

@app.route("/user_list")
def user_list():
    return render_template("user_list.html")

# 給料・token 登録
@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        shift_hour = float(request.form["shift_hour"])
        salary_per_hour = int(request.form["salary_per_hour"])

        save_wage(session["username"], shift_hour, salary_per_hour)

        return redirect(url_for("top"))

    return render_template("wage_register.html")

@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("game.html")


@app.route("/shift_register")
def shift_register():
    return render_template("shift_register.html")

if __name__ == "__main__":
    app.run(debug=True)
