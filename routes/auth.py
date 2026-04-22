from flask import Blueprint, render_template, request, redirect, session
from models.db import get_db

auth = Blueprint("auth", __name__)

# LOGIN
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

    return render_template("login.html")


# REGISTER
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()

        username = request.form["username"]
        password = request.form["password"]
        salary = float(request.form["salary"])

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        user_id = cursor.lastrowid

        # SAVE SALARY
        cursor.execute(
            "INSERT INTO budgets (user_id, daily_limit, monthly_limit, salary) VALUES (?, 0, 0, ?)",
            (user_id, salary)
        )

        conn.commit()

        return redirect("/login")

    return render_template("register.html")