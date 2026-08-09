"""SQLite storage layer for journal-server."""

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.environ.get("JOURNAL_DB", "journal.db"))

_local = threading.local()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = _connect()
        _local.conn = conn
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db():
    conn = _connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                body TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (id, user_id)
            );
            CREATE INDEX IF NOT EXISTS idx_entries_user ON entries(user_id);
            """
        )
        conn.commit()
    finally:
        conn.close()
