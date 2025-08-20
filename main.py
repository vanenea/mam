from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "finance.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    user TEXT,
                    account TEXT,
                    amount REAL
                )''')
    conn.commit()
    conn.close()

init_db()

# 首页
@app.route("/")
def index():
    return render_template("index.html")

# 添加数据
@app.route("/add", methods=["POST"])
def add_record():
    date = request.form.get("date")
    user = request.form.get("user")
    account = request.form.get("account")
    amount = float(request.form.get("amount"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO records (date, user, account, amount) VALUES (?, ?, ?, ?)",
              (date, user, account, amount))
    conn.commit()
    conn.close()
    return redirect("/")

# 获取数据（前端画图用）
@app.route("/data")
def get_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, user, SUM(amount) FROM records GROUP BY date, user ORDER BY date")
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
def records_page():
    date = request.args.get("date")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if date:
        c.execute("SELECT id, date, user, account, amount FROM records WHERE date=?", (date,))
    else:
        c.execute("SELECT id, date, user, account, amount FROM records ORDER BY date DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return render_template("records.html", records=rows, date=date)

# ==================
# 新增：修改记录
# ==================
@app.route("/update", methods=["POST"])
def update_record():
    record_id = request.form.get("id")
    user = request.form.get("user")
    account = request.form.get("account")
    amount = request.form.get("amount")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE records SET user=?, account=?, amount=? WHERE id=?",
              (user, account, amount, record_id))
    conn.commit()
    conn.close()
    return redirect("/records")

# ==================
# 新增：账户维度数据接口
# ==================
@app.route("/account-data")
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)