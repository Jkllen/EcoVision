import sqlite3
from datetime import datetime

DB_PATH = "eco_detections.db"

def create_table():
    """Create the detections table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            material TEXT,
            co2_kg REAL,
            biodegradable INTEGER,
            confidence REAL,
            frame_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_detection(material, co2_kg, biodegradable, confidence, frame_id):
    """Insert a new detection record"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('''
        INSERT INTO detections (timestamp, material, co2_kg, biodegradable, confidence, frame_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, material, co2_kg, int(biodegradable), confidence, frame_id))
    conn.commit()
    conn.close()
