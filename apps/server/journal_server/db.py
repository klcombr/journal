"""Storage layer: SQLite (default, local) or PostgreSQL (Supabase/Render).

Select the backend with the environment variable:

- `JOURNAL_DB`            -> SQLite file (default `journal.db`)
- `JOURNAL_DATABASE_URL`  -> PostgreSQL URL (`postgres://` or `postgresql://`),
                             falls back to `DATABASE_URL`.

The Postgres path uses a thin connection wrapper that translates the `?`
placeholders used in the query layer to `%s`, so the rest of the app is
backend-agnostic.
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

_PG_URL = os.environ.get("JOURNAL_DATABASE_URL") or os.environ.get("DATABASE_URL", "")
_IS_PG = _PG_URL.startswith("postgres://") or _PG_URL.startswith("postgresql://")

DB_PATH = Path(os.environ.get("JOURNAL_DB", "journal.db"))

_local = threading.local()

_SQLITE_SCHEMA = [
    "CREATE TABLE IF NOT EXISTS users ("
    " id INTEGER PRIMARY KEY AUTOINCREMENT,"
    " username TEXT NOT NULL UNIQUE,"
    " password_hash TEXT NOT NULL,"
    " created_at TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS entries ("
    " id TEXT NOT NULL,"
    " user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,"
    " body TEXT NOT NULL DEFAULT '',"
    " created_at TEXT NOT NULL,"
    " updated_at TEXT NOT NULL,"
    " deleted INTEGER NOT NULL DEFAULT 0,"
    " PRIMARY KEY (id, user_id))",
    "CREATE INDEX IF NOT EXISTS idx_entries_user ON entries(user_id)",
]

_PG_SCHEMA = [
    "CREATE TABLE IF NOT EXISTS users ("
    " id SERIAL PRIMARY KEY,"
    " username TEXT NOT NULL UNIQUE,"
    " password_hash TEXT NOT NULL,"
    " created_at TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS entries ("
    " id TEXT NOT NULL,"
    " user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,"
    " body TEXT NOT NULL DEFAULT '',"
    " created_at TEXT NOT NULL,"
    " updated_at TEXT NOT NULL,"
    " deleted INTEGER NOT NULL DEFAULT 0,"
    " PRIMARY KEY (id, user_id))",
    "CREATE INDEX IF NOT EXISTS idx_entries_user ON entries(user_id)",
]


if _IS_PG:
    import psycopg
    from psycopg.rows import dict_row

    def _connect():
        conn = psycopg.connect(
            _PG_URL,
            row_factory=dict_row,
            connect_timeout=15,
        )
        return _PGConnection(conn)

    class _PGConnection:
        """Minimal sqlite3-compatible wrapper around a psycopg connection."""

        def __init__(self, conn):
            self._conn = conn

        def execute(self, sql, params=()):
            return self._conn.execute(sql.replace("?", "%s"), params)

        def commit(self):
            self._conn.commit()

        def rollback(self):
            self._conn.rollback()

        def close(self):
            self._conn.close()

else:

    def _connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn


@contextmanager
def get_db():
    # Postgres: one connection per request (no idle connections leaking).
    if _IS_PG:
        conn = _connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return
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
        schema = _PG_SCHEMA if _IS_PG else _SQLITE_SCHEMA
        for stmt in schema:
            conn.execute(stmt)
        conn.commit()
    finally:
        conn.close()
