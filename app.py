from flask import Flask, render_template, request
import os
import requests

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from parser.log_parser import parse_logs
from detectors.brute_force import detect_bruteforce

app = Flask(__name__)


# 🌍 Geolocation function
def get_geo(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()

        return {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown")
        }
    except:
        return {
            "country": "Unknown",
            "city": "Unknown"
        }


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['logfile']

    filepath = os.path.join("logs", file.filename)
    file.save(filepath)

    # 🔍 Parse logs (NOW RETURNS TIMELINE TOO)
    failed_logins, timeline = parse_logs(filepath)

    # 🚨 Detect attacks
    alerts = detect_bruteforce(failed_logins)

    # 🌍 Add geolocation to alerts
    for alert in alerts:
        geo = get_geo(alert["ip"])
        alert["city"] = geo["city"]
        alert["country"] = geo["country"]

    # 📊 Summary stats
    total_failed = sum(failed_logins.values())

    most_dangerous_ip = None
    max_attempts = 0

    for ip, count in failed_logins.items():
        if count > max_attempts:
            max_attempts = count
            most_dangerous_ip = ip

    summary = {
        "total_failed": total_failed,
        "most_dangerous_ip": most_dangerous_ip,
        "max_attempts": max_attempts
    }

    # 📈 FINAL RENDER (includes timeline)
    return render_template(
        "results.html",
        alerts=alerts,
        summary=summary,
        timeline=timeline
    )


if __name__ == "__main__":
    app.run(debug=True)
