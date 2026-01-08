from flask import Flask, render_template, request, redirect, url_for, session
# modelsフォルダからモジュールをインポート
from routes import shift_manager
from routes import user_manager 

app = Flask(__name__)
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

        # user_managerを使って登録
        if user_manager.register_user(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="そのユーザ名は既に使われています")

    return render_template("register.html")


@app.route("/top")
def top():
    weekly_data = shift_manager.get_weekly_shift()
    return render_template("top.html", shift=weekly_data)


@app.route("/user_list")
def user_list():
    # user_managerからユーザー一覧を取得
    current_users = user_manager.get_users()
    return render_template("user_list.html", users=current_users)


@app.route("/wage_register", methods=["GET", "POST"])
def wage_register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # HTML修正後に shift_hour も受け取る前提です
        # エラー回避のため、安全に取得するように .get を使い、デフォルト値を設定しても良いですが
        # 基本はHTML側を修正してください。
        try:
            shift_hour = float(request.form["shift_hour"])
            salary_per_hour = int(request.form["salary_per_hour"])
            
            # user_managerを使って計算・保存
            user_manager.save_wage(session["username"], shift_hour, salary_per_hour)
            
            return redirect(url_for("top"))
        except KeyError:
            # HTMLが未修正の場合のエラーハンドリング（任意）
            return "HTMLファイルの修正が必要です（shift_hourがありません）"

    return render_template("wage_register.html")


@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))
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