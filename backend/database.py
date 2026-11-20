from pathlib import Path
import sqlite3
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent / "network.db"

def connect():
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE UNIQUE,
          ip_address TEXT NOT NULL UNIQUE, mac_address TEXT NOT NULL DEFAULT '',
          status TEXT NOT NULL CHECK(status IN ('online','offline')),
          connected_website TEXT NOT NULL DEFAULT '', x REAL, y REAL,
          created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
          updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE TABLE IF NOT EXISTS connections (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source_device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
          target_device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
          created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
          CHECK(source_device_id < target_device_id), UNIQUE(source_device_id,target_device_id)
        );
        """)

