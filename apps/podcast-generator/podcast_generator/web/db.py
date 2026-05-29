from __future__ import annotations

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = os.getenv("DB_PATH", "podcast.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL DEFAULT '',
                date TEXT NOT NULL,
                audio_path TEXT NOT NULL,
                script_path TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                picture TEXT NOT NULL DEFAULT '',
                provider TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def add_episode(
    title: str,
    url: str,
    date: str,
    audio_path: str,
    script_path: str = "",
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO episodes (title, url, date, audio_path, script_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, url, date, audio_path, script_path, datetime.now().isoformat()),
        )
        return cursor.lastrowid


def get_episodes(limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM episodes ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_episode(episode_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM episodes WHERE id = ?", (episode_id,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def get_user(user_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def create_user(
    email: str, name: str, picture: str, provider: str, provider_id: str
) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO users (email, name, picture, provider, provider_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email, name, picture, provider, provider_id, datetime.now().isoformat()),
        )
        return dict(
            conn.execute(
                "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        )
