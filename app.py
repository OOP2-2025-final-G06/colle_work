from flask import Flask, render_template, request, redirect, url_for, session

# ★ routesフォルダからインポートするように変更
from routes import shift_manager
from routes import user_manager
from routes import wage_manager
from routes import game_manager

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

app.register_blueprint(game_manager.game_bp)
game_manager.init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # user_managerを使って認証
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

        # user_managerを使って登録判定
        if user_manager.register_user(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="そのユーザ名は既に使われています")

    return render_template("register.html")


@app.route("/top")
def top():
    # 現在ログインしているユーザーを全処理のキーとして扱う
    username = session["username"]

    # 直近一週間分のシフトを取得
    weekly_data = shift_manager.get_weekly_shift(username)

    #　給料表示、ゲーム連携用のトークンを取得
    # wage_manager側も同様にusernameを渡してトークンを取得
    token = wage_manager.get_user_token(username)

    return render_template("top.html", shift=weekly_data, token=token)


@app.route("/user_list")
def user_list():
    # user_managerからユーザー一覧を取得
    all_users = user_manager.get_users()
    # ユーザーごとのシフト情報を取得
    user_shifts = {}
    for username in all_users:
        user_shifts[username] = shift_manager.get_weekly_shift_time_map(username)
    return render_template("user_list.html",
                            users=all_users,
                            user_tokens=user_manager.user_tokens,  # ユーザーごとのトークン数の追加
                            user_shifts=user_shifts # ユーザーごとのシフト情報を追加
                            )


@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            shift_hour = float(request.form["shift_hour"])

            # ② wage_manager に給料計算・保存を任せる
            salary, token = wage_manager.save_wage(
                session["username"],
                shift_hour
            )

            return redirect(url_for("top"))

        except KeyError:
            return "HTMLファイルの修正が必要です（shift_hourがありません）"

    # ③ 現在の時給を取得してHTMLに渡す
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
         # シフト登録と給料計算をまとめて manager に任せる
        shift_manager.save_shift_and_wage(username, request.form)
        return redirect(url_for("top"))

    # 来週分のシフト登録に必要な情報を一括取得
    data = shift_manager.get_shift_registration_data(username)
    
    return render_template("shift_register.html", data=data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)