from flask import Flask, render_template, request, redirect, session
import csv
import os
from datetime import datetime

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

app.secret_key = "finance-secret"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        session["user"] = username

        user_file = os.path.join(DATA_DIR, f"{username}.csv")

        if not os.path.exists(user_file):
            with open(user_file, "w", newline="") as f:
                csv.writer(f).writerow(["date","type","category","amount"])

        return redirect("/")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    CSV_PATH = os.path.join(DATA_DIR, f"{username}.csv")

    transactions = []
    balance = 0
    income = 0
    expense = 0

    if os.path.exists(CSV_PATH):

        with open(CSV_PATH, "r") as f:

            for r in csv.DictReader(f):

                amt = float(r["amount"])
                transactions.append(r)

                if r["type"] == "income":
                    income += amt
                    balance += amt
                else:
                    expense += abs(amt)
                    balance -= abs(amt)

    return render_template(
        "dashboard.html",
        t=transactions,
        b=balance,
        i=income,
        e=expense,
        username=username
    )


# ---------------- ADD INCOME ----------------
@app.route("/income", methods=["GET","POST"])
def income_page():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    CSV_PATH = os.path.join(DATA_DIR, f"{username}.csv")

    if request.method == "POST":

        with open(CSV_PATH, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.today().strftime("%Y-%m-%d"),
                "income",
                request.form["category"],
                request.form["amount"]
            ])

        return redirect("/")

    return render_template("add_income.html")


# ---------------- ADD EXPENSE ----------------
@app.route("/expense", methods=["GET","POST"])
def expense_page():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]
    CSV_PATH = os.path.join(DATA_DIR, f"{username}.csv")

    if request.method == "POST":

        with open(CSV_PATH, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.today().strftime("%Y-%m-%d"),
                "expense",
                request.form["category"],
                "-" + request.form["amount"]
            ])

        return redirect("/")

    return render_template("add_expense.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)