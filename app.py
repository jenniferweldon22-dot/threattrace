@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['logfile']

    filepath = os.path.join("logs", file.filename)
    file.save(filepath)

    failed_logins = parse_logs(filepath)
    alerts = detect_bruteforce(failed_logins)

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

    return render_template("results.html", alerts=alerts, summary=summary)
