from flask import Flask, render_template, request, redirect, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this-in-production"

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.cookie_name = "remember_token"
login_manager.cookie_duration = None

DB_NAME = "finance.db"


class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE id=?", (int(user_id),))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None


# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    user TEXT,
                    account TEXT,
                    amount REAL
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )""")

    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]

    if user_count == 0:
        hashed_password = generate_password_hash("admin123")
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", hashed_password),
        )

    conn.commit()
    conn.close()


init_db()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "SELECT id, username, password FROM users WHERE username=?", (username,)
        )
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], user[2])
            remember = request.form.get("remember") == "on"
            login_user(user_obj, remember=remember)
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# 首页
@app.route("/")
@login_required
def index():
    return render_template("index.html")


# 添加数据
@app.route("/add", methods=["POST"])
@login_required
def add_record():
    date = request.form.get("date")
    user = request.form.get("user")
    account = request.form.get("account")
    amount = float(request.form.get("amount"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO records (date, user, account, amount) VALUES (?, ?, ?, ?)",
        (date, user, account, amount),
    )
    conn.commit()
    conn.close()
    return redirect("/")


# 获取数据（前端画图用）
@app.route("/data")
@login_required
def get_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT date, user, SUM(amount) FROM records GROUP BY date, user ORDER BY date"
    )
    rows = c.fetchall()
    conn.close()

    data = {}
    for date, user, total in rows:
        if user not in data:
            data[user] = []
        data[user].append({"date": date, "total": total})

    # 总金额（两个用户合计）
    overall = {}
    for user, vals in data.items():
        for v in vals:
            d = v["date"]
            overall[d] = overall.get(d, 0) + v["total"]

    data["AllUsers"] = [{"date": d, "total": t} for d, t in overall.items()]

    return jsonify(data)


# ==================
# 新增：查询页面
# ==================
@app.route("/records")
@login_required
def records_page():
    date = request.args.get("date")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if date:
        c.execute(
            "SELECT id, date, user, account, amount FROM records WHERE date=?", (date,)
        )
    else:
        c.execute(
            "SELECT id, date, user, account, amount FROM records ORDER BY date DESC LIMIT 20"
        )
    rows = c.fetchall()
    conn.close()
    return render_template("records.html", records=rows, date=date)


# ==================
# 新增：修改记录
# ==================
@app.route("/update", methods=["POST"])
@login_required
def update_record():
    record_id = request.form.get("id")
    user = request.form.get("user")
    account = request.form.get("account")
    amount = request.form.get("amount")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE records SET user=?, account=?, amount=? WHERE id=?",
        (user, account, amount, record_id),
    )
    conn.commit()
    conn.close()
    return redirect("/records")


# ==================
# 新增：账户维度数据接口
# ==================
@app.route("/account-data")
@login_required
def account_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, user, account, amount FROM records ORDER BY date")
    rows = c.fetchall()
    conn.close()

    data = {}
    for date, user, account, amount in rows:
        key = f"{user}-{account}"
        if key not in data:
            data[key] = []
        data[key].append({"date": date, "amount": amount})

    return jsonify(data)


# ==================
# 新增：资金占比页面
# ==================
@app.route("/pie-chart")
@login_required
def pie_chart_page():
    return render_template("pie_chart.html")


# ==================
# 新增：资金占比数据接口
# ==================
@app.route("/pie-data")
@login_required
def pie_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT MAX(date) FROM records")
    latest_date = c.fetchone()[0]

    if latest_date:
        c.execute(
            "SELECT user, SUM(amount) as total FROM records WHERE date=? GROUP BY user",
            (latest_date,),
        )
        user_rows = c.fetchall()
        user_data = [{"name": user, "value": total} for user, total in user_rows]

        c.execute(
            "SELECT account, SUM(amount) as total FROM records WHERE date=? GROUP BY account",
            (latest_date,),
        )
        account_rows = c.fetchall()
        account_data = [
            {"name": account, "value": total} for account, total in account_rows
        ]
    else:
        user_data = []
        account_data = []

    conn.close()

    return jsonify({"users": user_data, "accounts": account_data})


# ==================
# 删除记录
# ==================
@app.route("/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    return redirect("/records")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
