import os
import sqlite3
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db")

def init_db():
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, event_type TEXT NOT NULL, message TEXT)")
        con.commit()
        con.close()
    except Exception as e:
        print("DB init error:", e)

def log_event(event_type, message=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("INSERT INTO events (ts, event_type, message) VALUES (?, ?, ?)",
                    (ts, event_type, str(message)))
        con.commit()
        con.close()
    except Exception as e:
        print("DB log error:", e)
    print("[" + ts + "] " + str(event_type) + ": " + str(message))

def get_events(limit=200):
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT ts, event_type, message FROM events ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        con.close()
        return rows
    except Exception:
        return []
