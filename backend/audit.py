import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "echogate.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            decision TEXT,
            reason TEXT,
            spoof_label TEXT,
            spoof_score REAL,
            identity_name TEXT,
            similarity REAL,
            latency_ms INTEGER,
            mode TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_decision(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_log (
            request_id, decision, reason,
            spoof_label, spoof_score,
            identity_name, similarity,
            latency_ms, mode, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["request_id"],
        data["decision"],
        data["reason"],
        data["spoof"]["label"],
        data["spoof"]["score"],
        data["identity"]["name"],
        data["identity"]["similarity"],
        data["latency_ms"],
        data["mode"],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()