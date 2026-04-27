def parse_logs(filepath):
    failed_logins = {}

    with open(filepath, 'r') as f:
        for line in f:
            if "Failed password" in line:
                parts = line.split()
                ip = parts[-1]

                if ip not in failed_logins:
                    failed_logins[ip] = 0

                failed_logins[ip] += 1

    return failed_logins