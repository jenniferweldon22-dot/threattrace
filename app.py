from flask import Flask, render_template, request, Response, redirect, url_for, session, jsonify
import os
import requests
import random
import time
import json
from functools import wraps

from parser.log_parser import parse_logs
from database import init_db, save_alert, authenticate_user, get_leaderboard, get_analytics_summary

app = Flask(__name__)

# =========================
# 🔐 CONFIG (STABLE FIX)
# =========================
app.secret_key = "change-this-to-a-strong-random-secret"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

init_db()


# =========================
# 🔐 AUTH DECORATOR
# =========================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# =========================
# 🌍 GEOLOCATION
# =========================
def get_geo(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        d = r.json()
        return {
            "country": d.get("country", "Unknown"),
            "city": d.get("city", "Unknown"),
            "lat": d.get("lat"),
            "lon": d.get("lon")
        }
    except:
        return {"country": "Unknown", "city": "Unknown", "lat": None, "lon": None}


# =========================
# 🧠 RISK ENGINE
# =========================
def calculate_risk(attempts):
    return max(0, min(100, attempts * 12 + random.randint(-5, 5)))


# =========================
# 🔑 LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = authenticate_user(username, password)

        if user:
            session["user"] = {
                "username": user["username"],
                "role": user["role"]
            }
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return redirect(url_for("dashboard"))


# =========================
# 📊 DASHBOARD
# =========================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        alerts=get_leaderboard(),
        summary=get_analytics_summary()
    )


# =========================
# 📁 ANALYZE LOGS
# =========================
@app.route("/analyze", methods=["POST"])
@login_required
def analyze():

    file = request.files.get("logfile")
    if not file:
        return "No file uploaded", 400

    os.makedirs("logs", exist_ok=True)

    path = os.path.join("logs", file.filename)
    file.save(path)

    failed, timeline = parse_logs(path)

    for ip, count in failed.items():

        geo = get_geo(ip)

        save_alert({
            "ip": ip,
            "city": geo["city"],
            "country": geo["country"],
            "lat": geo["lat"],
            "lon": geo["lon"],
            "count": count,
            "risk": calculate_risk(count)
        })

    return redirect(url_for("dashboard"))


# =========================
# 🌐 REAL-TIME SOC STREAM
# =========================
@app.route("/stream")
@login_required
def stream():

    def generate():
        while True:
            time.sleep(2)

            event = {
                "ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
                "city": "Live SOC",
                "country": "Stream",
                "lat": 25.0 + random.random(),
                "lon": 55.0 + random.random(),
                "risk": random.randint(10, 100),
                "count": random.randint(1, 50)
            }

            save_alert(event)

            yield f"data: {json.dumps(event)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


# =========================
# 📊 ANALYTICS API
# =========================
@app.route("/api/analytics")
@login_required
def api_analytics():
    return jsonify(get_analytics_summary())


# =========================
# 🚀 RUN SERVER (IMPORTANT FIX)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)