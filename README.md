# ThreatTrace 🔐

ThreatTrace is a lightweight cybersecurity log analysis tool that detects brute-force attacks from server logs and visualizes suspicious activity in a web dashboard.

## 🚀 Features
- Upload and analyze log files
- Detect failed login attempts
- Identify brute-force attack patterns
- Risk scoring system (0–100)
- Security dashboard with severity levels
- Summary statistics (total attacks, top IP, etc.)

## 🧠 How it works
1. User uploads a log file
2. System parses login attempts
3. Detection engine calculates risk score
4. Dashboard displays alerts and summary

## 📊 Example Output
- IP: 192.168.1.10
- Risk Score: 80/100
- Status: CRITICAL

## 🛠 Tech Stack
- Python (Flask)
- HTML / CSS
- Basic security analytics logic

## 🎯 Purpose
Built as a cybersecurity portfolio project to demonstrate log analysis, threat detection, and security dashboard design.

## 📌 Future Improvements
- IP geolocation mapping
- Real-time log streaming
- Export incident reports (PDF)
- Machine learning anomaly detection