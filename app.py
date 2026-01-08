from flask import Flask, render_template, request, redirect, url_for, session
import shift_manager

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# 仮のユーザ情報（後でDBに置き換え可能）
users = {
    "testuser": "password"
}


salary_per_hour = 1000


user_tokens = {
    "testuser": 0
}


wage_records = []


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
# ---------------------------------------


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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return render_template("register.html", error="そのユーザ名は既に使われています")
        else:
            users[username] = password
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/top")
def top():
    # 登録されたシフトデータを取得
    weekly_data = shift_manager.get_weekly_shift()
    # 画面（top.html）にデータを渡す
    return render_template("top.html", shift=weekly_data)


@app.route("/user_list")
def user_list():
    return render_template("user_list.html", users=users)



# mainブランチの「給料計算とトークン保存」のロジックを採用
@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # フォームからシフト時間と時給を取得
        shift_hour = float(request.form["shift_hour"])
        salary_per_hour = int(request.form["salary_per_hour"])

        # 計算して保存（mainブランチの関数を使用）
        save_wage(session["username"], shift_hour, salary_per_hour)

        return redirect(url_for("top"))

    return render_template("wage_register.html")
# ---------------------------------------------


@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("game.html")


@app.route("/shift_register", methods=["GET", "POST"])
def shift_register():
    if request.method == "POST":
        # データを保存する
        shift_manager.update_weekly_shift(request.form)
        return redirect(url_for("top"))
    
    # 保存されているデータを取得してHTMLに送る
    current_data = shift_manager.get_weekly_shift()
    return render_template("shift_register.html", shift=current_data)


if __name__ == "__main__":
    app.run(debug=True, port=8080)