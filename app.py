from flask import Flask, render_template, request, redirect, url_for
from models.shift_manager import ShiftManager 

app = Flask(__name__)

users = { "testuser": "password" }

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
    return render_template("top.html")

@app.route("/shift_register", methods=["GET", "POST"])
def shift_register():
    user_name = "testuser"
    manager = ShiftManager(user_name)

    # ★復活: URLパラメータから日付を取得
    debug_date = request.args.get("date")

    if request.method == "POST":
        input_date = request.form.get("shift_date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        
        manager.register_shift(input_date, start_time, end_time)
        
        # ★復活: 保存後も同じ日付を維持してリダイレクト
        if debug_date:
            return redirect(url_for("shift_register", date=debug_date))
        else:
            return redirect(url_for("shift_register"))

    context = manager.get_shift_data(debug_date_str=debug_date)
    return render_template("shift_register.html", **context)

@app.route("/user_list")
def user_list():
    return render_template("user_list.html")

@app.route("/wage_register")
def wage_register():
    return render_template("wage_register.html")

@app.route("/game")
def game():
    return render_template("game.html")

if __name__ == "__main__":
    app.run(debug=True, port=8080)