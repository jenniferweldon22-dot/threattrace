import re

def parse_logs(filepath):
    failed_logins = {}
    timeline = []

    with open(filepath, "r") as file:
        for line in file:

            # extract IP
            ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', line)
            ip = ip_match.group(1) if ip_match else None

            # extract timestamp (first part of line)
            time_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', line)
            timestamp = time_match.group(1) if time_match else "unknown"

            if ip:
                failed_logins[ip] = failed_logins.get(ip, 0) + 1

                timeline.append({
                    "ip": ip,
                    "time": timestamp
                })

    return failed_logins, timeline