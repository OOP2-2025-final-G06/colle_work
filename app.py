from flask import Flask, render_template, request, redirect, url_for, session

# ★ routesフォルダからインポートするように変更
from routes import shift_manager
from routes import user_manager
from routes import game_manager

app = Flask(__name__)
app.register_blueprint(game_manager.game_bp)  # game_managerのBlueprintを登録
app.secret_key = "secret_key_for_session"

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
    # shift_managerを使ってデータ取得
    weekly_data = shift_manager.get_weekly_shift()
    return render_template("top.html", shift=weekly_data)


@app.route("/user_list")
def user_list():
    # user_managerからユーザー一覧を取得
    all_users = user_manager.get_users()
    return render_template("user_list.html", users=all_users)


@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # HTML修正済み前提: shift_hourを取得
        try:
            shift_hour = float(request.form["shift_hour"])
            salary_per_hour = int(request.form["salary_per_hour"])
            
            # user_managerで計算・保存
            user_manager.save_wage(session["username"], shift_hour, salary_per_hour)
            
            return redirect(url_for("top"))
        except KeyError:
            # HTMLがまだ修正されていない場合の安全策
            return "エラー: wage_register.html に shift_hour の入力欄がありません。"

    return render_template("wage_register.html")


@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("game.html")


@app.route("/shift_register", methods=["GET", "POST"])
def shift_register():
    if request.method == "POST":
        # shift_managerを使って保存
        shift_manager.update_weekly_shift(request.form)
        return redirect(url_for("top"))
    
    current_data = shift_manager.get_weekly_shift()
    return render_template("shift_register.html", shift=current_data)


if __name__ == "__main__":
    app.run(debug=True, port=8080)