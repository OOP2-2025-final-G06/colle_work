# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime # 日付取得用にインポート

# routesフォルダからインポート
from routes import shift_manager
from routes import user_manager
from routes import wage_manager
from routes import game_manager

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

app.register_blueprint(game_manager.game_bp)
# DB初期化
user_manager.init_db()
game_manager.init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if user_manager.verify_user(username, password):
            session["username"] = username
            return redirect(url_for("top"))
        else:
            return render_template("login.html", error="ユーザ名かパスワードが間違っています")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if user_manager.register_user(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="そのユーザ名は既に使われています")
    return render_template("register.html")

@app.route("/top")
def top():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    # 1. カレンダー情報（今週・来週）を取得
    calendar_data = shift_manager.get_calendar_data(username)

    # 2. 現在のトークン、時給
    token = wage_manager.get_user_token(username)
    current_salary = wage_manager.get_salary(username)
    
    # 3. 給与実績（今月、今年）
    monthly_earnings = wage_manager.get_monthly_earnings(username)
    yearly_earnings = wage_manager.get_yearly_earnings(username)

    return render_template(
        "top.html",
        calendar=calendar_data,
        token=token,
        salary=current_salary,
        monthly_earnings=monthly_earnings,
        yearly_earnings=yearly_earnings
    )

@app.route("/user_list")
def user_list():
    all_users = user_manager.get_users()
    user_shifts = {}
    user_tokens = {}

    for username in all_users:
        user_shifts[username] = shift_manager.get_weekly_shift_time_map(username)
        user_tokens[username] = game_manager.get_user_token_from_db(username) # ゲームDBからトークン取得

    return render_template(
        "user_list.html",
        users=all_users,
        user_tokens=user_tokens,
        user_shifts=user_shifts
    )

@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        try:
            # フォームから「salary_per_hour」を受け取る
            new_salary = int(request.form["salary_per_hour"])
            wage_manager.set_salary(username, new_salary)
            return redirect(url_for("top"))
        except (KeyError, ValueError):
            current_salary = wage_manager.get_salary(username)
            return render_template("wage_register.html", salary=current_salary, error="金額を正しく入力してください")

    current_salary = wage_manager.get_salary(username)
    return render_template("wage_register.html", salary=current_salary)

@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("game.html")

@app.route("/shift_register", methods=["GET", "POST"])
def shift_register():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        shift_manager.save_shift_and_wage(username, request.form)
        return redirect(url_for("top"))
    data = shift_manager.get_shift_registration_data(username)
    return render_template("shift_register.html", data=data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)