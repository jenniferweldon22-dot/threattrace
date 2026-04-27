def detect_bruteforce(failed_logins, threshold=1):
    alerts = []

    for ip, count in failed_logins.items():

        # 🔥 Risk score calculation
        risk_score = min(count * 25, 100)

        # 🚨 Risk classification
        if risk_score >= 80:
            risk = "CRITICAL"
        elif risk_score >= 50:
            risk = "HIGH"
        elif risk_score >= 25:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # 🚨 Always create alerts for demo visibility
        if count >= threshold:
            alerts.append({
                "ip": ip,
                "count": count,
                "risk": risk,
                "score": risk_score,
                "message": "Possible brute force attack detected"
            })

    return alerts