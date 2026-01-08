from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta
import shift_manager

app = Flask(__name__)

# 仮のユーザ情報（後でDBに置き換え可能）
users = {
    "testuser": "password"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
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
    # 今日
    today = date.today()

    # 今週の月曜日
    monday = today - timedelta(days=today.weekday())

    # 今週（月〜日）の日付データ作成
    week = []
    for i in range(7):
        d = monday + timedelta(days=i)
        week.append({
            "date": d,
            "md": d.strftime("%m/%d"),
            "weekday": d.weekday()  # 月=0
        })

    # 登録されたシフトを取得
    weekly_shift = shift_manager.get_weekly_shift()

    return render_template(
        "top.html",
        week=week,
        shift=weekly_shift,
        today=today
    )


@app.route("/user_list")
def user_list():
    # 全ユーザーの来週のシフトを取得
    weekly_shift = shift_manager.get_weekly_shift()
    return render_template("user_list.html", users=users, shift=weekly_shift)


@app.route("/wage_register")
def wage_register():
    return render_template("wage_register.html")


@app.route("/game")
def game():
    return render_template("game.html")


@app.route("/shift_register", methods=["GET", "POST"])
def shift_register():
    if request.method == "POST":
        shift_manager.update_weekly_shift(request.form)
        return redirect(url_for("top"))

    current_data = shift_manager.get_weekly_shift()
    return render_template("shift_register.html", shift=current_data)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
