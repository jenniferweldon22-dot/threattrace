import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "threattrace.db"


# =========================
# DB CONNECTION
# =========================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# INIT DATABASE (SAAS READY)
# =========================
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # ORGANIZATIONS (SAAS CORE)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orgs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =========================
    # USERS TABLE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'analyst',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =========================
    # ALERTS TABLE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER,
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

    conn.commit()
    conn.close()


# =========================
# CREATE ORGANIZATION
# =========================
def create_org(name):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO orgs (name)
        VALUES (?)
    """, (name,))

    conn.commit()
    conn.close()


# =========================
# CREATE USER (SAAS)
# =========================
def create_user(username, password, org_id=1, role="analyst"):
    conn = get_db()
    cursor = conn.cursor()

    hashed = generate_password_hash(password)

    try:
        cursor.execute("""
            INSERT INTO users (username, password, org_id, role)
            VALUES (?, ?, ?, ?)
        """, (username, hashed, org_id, role))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    finally:
        conn.close()


# =========================
# AUTHENTICATION
# =========================
def authenticate_user(username, password):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return dict(user)

    return None


# =========================
# SAVE ALERT (ORG-AWARE)
# =========================
def save_alert(alert):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (
            org_id, ip, city, country, lat, lon, risk, count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        alert.get("org_id", 1),
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
# LEADERBOARD (PER ORG)
# =========================
def get_leaderboard(org_id, limit=10):
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
        WHERE org_id = ?
        GROUP BY ip
        ORDER BY max_risk DESC, total_attempts DESC
        LIMIT ?
    """, (org_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


# =========================
# ANALYTICS (PER ORG)
# =========================
def get_analytics_summary(org_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alerts
        WHERE org_id = ?
    """, (org_id,))
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS high
        FROM alerts
        WHERE org_id = ? AND risk >= 80
    """, (org_id,))
    high = cursor.fetchone()["high"]

    cursor.execute("""
        SELECT ip, MAX(risk) AS risk
        FROM alerts
        WHERE org_id = ?
        GROUP BY ip
        ORDER BY risk DESC
        LIMIT 1
    """, (org_id,))

    top = cursor.fetchone()

    conn.close()

    return {
        "total_events": total,
        "high_risk": high,
        "top_ip": top["ip"] if top else "N/A"
    }