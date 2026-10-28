import sqlite3
from datetime import datetime

DB_NAME = "aerosora_uas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS uas_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        pilot_id TEXT,
        uas_callsign TEXT,
        mission_label TEXT,
        mtow_kg REAL,
        altitude_m REAL,
        proximity_crowd INTEGER,
        risk_index INTEGER,
        operational_category TEXT,
        flight_decision TEXT,
        directives TEXT
    )
    """)
    conn.commit()
    conn.close()

def persist_mission(pilot_id, callsign, label, mtow, alt, crowd, score, category, decision, directives_json):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO uas_assessments 
        (timestamp, pilot_id, uas_callsign, mission_label, mtow_kg, altitude_m, proximity_crowd, risk_index, operational_category, flight_decision, directives)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), pilot_id, callsign, label, mtow, alt, crowd, score, category, decision, directives_json))
    conn.commit()
    conn.close()

def query_all_missions():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM uas_assessments ORDER BY id DESC")
    records = cur.fetchall()
    conn.close()
    return [dict(r) for r in records]

if __name__ == "__main__":
    init_db()
    print("[DB] Initialized AeroSORA SQLite Database successfully.")