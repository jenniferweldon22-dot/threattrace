import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "threattrace.db"


# =========================
# CONNECTION
# =========================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# INIT DATABASE (SOC STRUCTURE)
# =========================
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # ALERTS TABLE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL,
        city TEXT,
        country TEXT,
        lat REAL,
        lon REAL,
        risk INTEGER DEFAULT 0,
        count INTEGER DEFAULT 1,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =========================
    # USERS TABLE (SOC AUTH)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'analyst'
    )
    """)

    conn.commit()
    conn.close()


# =========================
# CREATE USER (ADMIN TOOL)
# =========================
def create_user(username, password, role="analyst"):
    conn = get_db()
    cursor = conn.cursor()

    hashed = generate_password_hash(password)

    try:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, hashed, role))

        conn.commit()

    except sqlite3.IntegrityError:
        # user already exists
        pass

    finally:
        conn.close()


# =========================
# AUTH USER
# =========================
def authenticate_user(username, password):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):
        return dict(user)

    return None


# =========================
# SAVE ALERT (SOC INGESTION)
# =========================
def save_alert(alert):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (ip, city, country, lat, lon, risk, count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        alert.get("ip", "unknown"),
        alert.get("city", "Unknown"),
        alert.get("country", "Unknown"),
        alert.get("lat"),
        alert.get("lon"),
        alert.get("risk", 0),
        alert.get("count", 1)
    ))

    conn.commit()
    conn.close()


# =========================
# LEADERBOARD (SOC CORE FEATURE)
# =========================
def get_leaderboard(limit=10):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            ip,
            city,
            country,
            SUM(count) AS total_attempts,
            MAX(risk) AS max_risk
        FROM alerts
        GROUP BY ip, city, country
        ORDER BY max_risk DESC, total_attempts DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


# =========================
# SOC ANALYTICS SUMMARY
# =========================
def get_analytics_summary():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM alerts")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS high FROM alerts WHERE risk >= 80")
    high = cursor.fetchone()["high"]

    cursor.execute("""
        SELECT ip, MAX(risk) AS risk
        FROM alerts
        GROUP BY ip
        ORDER BY risk DESC
        LIMIT 1
    """)
    top_ip = cursor.fetchone()

    conn.close()

    return {
        "total_events": total,
        "high_risk": high,
        "top_ip": top_ip["ip"] if top_ip else "N/A"
    }