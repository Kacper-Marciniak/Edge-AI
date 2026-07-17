import sqlite3
import json

DB_PATH = "P6/logs.db"
EVENTS_PATH = "P6/example_logs.json"

def init_sql_database():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        f"""
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY,
            time TEXT UNIQUE,
            level TEXT,
            message TEXT
        )
        """
    )
    db.commit()
    db.close()

def add_event_to_database(event: dict):
    db = sqlite3.connect(DB_PATH)
    db.execute(
        f"""
        INSERT OR IGNORE INTO logs
        (time, level, message)
        VALUES (?, ?, ?)
        """,
        (
            event["time"],
            event["level"].upper(),
            event["message"]
        )
    )
    db.commit()
    db.close()

def load_events_from_json(json_path: str = EVENTS_PATH):
    with open(json_path, "r", encoding="utf-8") as f:
        events = json.load(f)
    for event in events:
        add_event_to_database(event)

def analyze_logs():
    db = sqlite3.connect(DB_PATH)
    report = {}

    cursor = db.cursor()    
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM logs
        """
    )
    report["total_events"] = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT level, COUNT(*)
        FROM logs
        GROUP BY level
        ORDER BY COUNT(*) DESC
        """
    )
    report["levels"] = dict(cursor.fetchall())

    cursor.execute(
        """
        SELECT time, message
        FROM logs
        WHERE level='ERROR'
        ORDER BY time DESC
        LIMIT 1
        """
    )
    last_error = cursor.fetchone()
    report["last_error"] = None
    if last_error:
        report["last_error"] = {
            "time": last_error[0],
            "message": last_error[1]
        }

    cursor.execute(
        """
        SELECT time, message
        FROM logs
        WHERE level='ERROR'
        ORDER BY time DESC
        LIMIT 5
        """
    )
    report["critical_events"] = [
        {
            "time": row[0],
            "message": row[1]
        }
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT MIN(time), MAX(time)
        FROM logs
        """
    )
    time_range = cursor.fetchone()
    report["time_range"] = {
        "from": time_range[0],
        "to": time_range[1]
    }

    db.close()
    return report