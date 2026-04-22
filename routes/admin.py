from flask import Blueprint, render_template, request, redirect, session
from models.db import get_db

# ✅ DEFINE BLUEPRINT FIRST (VERY IMPORTANT)
admin = Blueprint("admin", __name__)

ADMIN_USERNAME = "admin123"
ADMIN_PASSWORD = "12345"


# ========================
# ADMIN LOGIN
# ========================
@admin.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            return redirect("/admin-dashboard")

    return render_template("admin_login.html")


# ========================
# ADMIN DASHBOARD + ANALYTICS
# ========================
@admin.route("/admin-dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    # 📊 GLOBAL STATS
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spent = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(salary) FROM budgets")
    total_salary = cursor.fetchone()[0] or 0

    # 👤 USERS
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    user_data = []

    for user in users:
        user_id = user["id"]

        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id=?",
            (user_id,)
        )
        spent = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT daily_limit, monthly_limit, salary FROM budgets WHERE user_id=?",
            (user_id,)
        )
        limits = cursor.fetchone()

        daily = limits["daily_limit"] if limits else 0
        monthly = limits["monthly_limit"] if limits else 0
        salary = limits["salary"] if limits else 0

        user_data.append({
            "id": user_id,
            "username": user["username"],
            "daily": daily,
            "monthly": monthly,
            "salary": salary,
            "spent": spent
        })

    return render_template(
        "admin_dashboard.html",
        users=user_data,
        total_users=total_users,
        total_spent=total_spent,
        total_salary=total_salary
    )


# ========================
# DELETE USER
# ========================
@admin.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    cursor.execute("DELETE FROM expenses WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM budgets WHERE user_id=?", (user_id,))

    conn.commit()

    return redirect("/admin-dashboard")