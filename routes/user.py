from flask import Blueprint, render_template, request, redirect, session
from models.db import get_db
from datetime import datetime
from collections import defaultdict

user = Blueprint("user", __name__)


# ========================
# DASHBOARD
# ========================
@user.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    user_id = session["user_id"]

    # ========================
    # HANDLE FORMS
    # ========================
    if request.method == "POST":

        # ADD EXPENSE
        if "amount" in request.form:
            amount = float(request.form["amount"])
            category = request.form["category"]
            custom = request.form.get("custom_category")
            date = request.form["date"]

            if category == "Other" and custom:
                category = custom

            cursor.execute(
                "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                (user_id, amount, category, date)
            )
            conn.commit()

        # SET DAILY LIMIT
        if "daily_limit" in request.form:
            new_limit = float(request.form["daily_limit"])

            cursor.execute("SELECT * FROM budgets WHERE user_id=?", (user_id,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE budgets SET daily_limit=? WHERE user_id=?",
                    (new_limit, user_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO budgets (user_id, daily_limit, monthly_limit, salary) VALUES (?, ?, ?, ?)",
                    (user_id, new_limit, 0, 0)
                )

            conn.commit()

    # ========================
    # FETCH DATA
    # ========================
    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))
    expenses = cursor.fetchall()

    cursor.execute("SELECT * FROM budgets WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    salary = data["salary"] if data else 0
    user_daily_limit = data["daily_limit"] if data else 0

    # ========================
    # CALCULATIONS
    # ========================
    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")

    daily_total = sum(e["amount"] for e in expenses if e["date"] == today)
    monthly_total = sum(e["amount"] for e in expenses if e["date"].startswith(current_month))

    needs = salary * 0.5
    wants = salary * 0.25
    savings = salary * 0.15
    investment = salary * 0.10

    ideal_daily = (needs + wants) / 30 if salary else 0
    monthly_limit = needs + wants

    # ========================
    # WARNING
    # ========================
    warning = None

    if user_daily_limit and (user_daily_limit - daily_total) <= 150:
        warning = f"⚠️ Only ₹{round(user_daily_limit - daily_total, 2)} left for today!"

    if monthly_limit and (monthly_limit - monthly_total) <= 5000:
        warning = f"⚠️ Only ₹{round(monthly_limit - monthly_total, 2)} left this month!"

    # ========================
    # CHART DATA
    # ========================
    category_data = defaultdict(float)
    for e in expenses:
        category_data[e["category"]] += e["amount"]

    labels = list(category_data.keys())
    values = list(category_data.values())

    monthly_data = defaultdict(float)
    for e in expenses:
        key = e["date"][:7]
        monthly_data[key] += e["amount"]

    months = list(monthly_data.keys())
    monthly_totals = list(monthly_data.values())

    return render_template(
        "user_dashboard.html",
        username=session["username"],
        expenses=expenses,
        daily_total=daily_total,
        monthly_total=monthly_total,
        daily_limit=user_daily_limit,
        ideal_daily=round(ideal_daily, 2),
        monthly_limit=round(monthly_limit, 2),
        salary=salary,
        needs=needs,
        wants=wants,
        savings=savings,
        investment=investment,
        warning=warning,
        labels=labels,
        values=values,
        months=months,
        monthly_totals=monthly_totals
    )


# ========================
# SAFE DELETE EXPENSE
# ========================
@user.route("/delete/<int:expense_id>")
def delete_expense(expense_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    user_id = session["user_id"]

    # ✅ Only delete user's own expense
    cursor.execute(
        "DELETE FROM expenses WHERE id=? AND user_id=?",
        (expense_id, user_id)
    )

    conn.commit()
    return redirect("/dashboard")


# ========================
# UPDATE SALARY
# ========================
@user.route("/update-salary", methods=["GET", "POST"])
def update_salary():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    user_id = session["user_id"]

    if request.method == "POST":
        new_salary = float(request.form["salary"])

        cursor.execute("SELECT * FROM budgets WHERE user_id=?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE budgets SET salary=? WHERE user_id=?",
                (new_salary, user_id)
            )
        else:
            cursor.execute(
                "INSERT INTO budgets (user_id, daily_limit, monthly_limit, salary) VALUES (?, ?, ?, ?)",
                (user_id, 0, 0, new_salary)
            )

        conn.commit()
        return redirect("/dashboard")

    return render_template("update_salary.html")