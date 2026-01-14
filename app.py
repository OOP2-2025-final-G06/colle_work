from flask import Flask, render_template, request, redirect, url_for, session

from routes import shift_manager
from routes import user_manager
from routes import wage_manager
from routes import game_manager
from routes import db as db_module

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# DB 初期化（全テーブル）
db_module.init_db()
# ゲーム側は独自 DB を使っているため初期化
app.register_blueprint(game_manager.game_bp)
game_manager.init_db()
# shift_manager は database.db を利用するので念のため初期化
shift_manager.init_db()

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
    weekly_data = shift_manager.get_weekly_shift(username)
    token = user_manager.get_user_token(username)
    return render_template("top.html", shift=weekly_data, token=token)


@app.route("/user_list")
def user_list():
    if "username" not in session:
        return redirect(url_for("login"))

    all_users = user_manager.get_users()
    user_shifts = {}
    for username in all_users:
        user_shifts[username] = shift_manager.get_weekly_shift_time_map(username)
    return render_template("user_list.html",
                            users=all_users,
                            user_tokens=user_manager.get_all_user_tokens(),
                            user_shifts=user_shifts
                            )


@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            shift_hour = float(request.form["shift_hour"])
            salary, token = wage_manager.save_wage(
                session["username"],
                shift_hour
            )
            return redirect(url_for("top"))
        except KeyError:
            return "HTMLファイルの修正が必要です（shift_hourがありません）"

    salary_per_hour = wage_manager.get_salary()
    return render_template(
        "wage_register.html",
        salary_per_hour=salary_per_hour
    )

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