"""SQLite database layer for motedico."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent.parent
_default_db = str(_APP_DIR / "data" / "motedico.db")
DB_PATH = os.getenv("MOTEDICO_DB_PATH", _default_db)


@contextmanager
def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
