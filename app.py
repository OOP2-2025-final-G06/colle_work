from flask import Flask, render_template, request, redirect, url_for

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
    return render_template("top.html")


@app.route("/user_list")
def user_list():
    return render_template("user_list.html")


@app.route("/wage_register")
def wage_register():
    return render_template("wage_register.html")


@app.route("/game")
def game():
    return render_template("game.html")


@app.route("/shift_register")
def shift_register():
    return render_template("shift_register.html")


if __name__ == "__main__":
    app.run(debug=True,port=8080)
