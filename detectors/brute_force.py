def detect_bruteforce(failed_logins, threshold=3):
    alerts = []

    for ip, count in failed_logins.items():

        # 🔥 Risk score calculation (IMPORTANT PART)
        risk_score = min(count * 10, 100)

        if risk_score >= 80:
            risk = "CRITICAL"
        elif risk_score >= 50:
            risk = "HIGH"
        elif risk_score >= threshold * 10:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        if count >= threshold:
            alerts.append({
                "ip": ip,
                "count": count,
                "risk": risk,
                "score": risk_score,
                "message": "Possible brute force attack detected"
            })

    return alerts