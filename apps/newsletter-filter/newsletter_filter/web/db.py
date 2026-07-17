from __future__ import annotations

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

_APP_DIR = Path(__file__).resolve().parent.parent.parent
_default_db = str(_APP_DIR / "data" / "newsletter_filter.db")
DB_PATH = os.getenv("FILTER_DB_PATH", _default_db)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                llm_provider TEXT NOT NULL,
                llm_model TEXT NOT NULL,
                llm_api_key TEXT,
                imap_host TEXT,
                imap_user TEXT,
                imap_password TEXT,
                imap_folder TEXT,
                rss_urls TEXT,
                default_query TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                date TEXT,
                relevant INTEGER DEFAULT 0,
                score REAL DEFAULT 0.0,
                summary TEXT,
                key_points TEXT,
                justification TEXT,
                created_at TEXT NOT NULL
            )
        """)


def get_db_settings() -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        return dict(row) if row else None


def save_db_settings(settings_data: Dict[str, Any]):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO settings (
                id, llm_provider, llm_model, llm_api_key,
                imap_host, imap_user, imap_password, imap_folder,
                rss_urls, default_query
            ) VALUES (1, :llm_provider, :llm_model, :llm_api_key,
                      :imap_host, :imap_user, :imap_password, :imap_folder,
                      :rss_urls, :default_query)
            ON CONFLICT(id) DO UPDATE SET
                llm_provider=excluded.llm_provider,
                llm_model=excluded.llm_model,
                llm_api_key=excluded.llm_api_key,
                imap_host=excluded.imap_host,
                imap_user=excluded.imap_user,
                imap_password=excluded.imap_password,
                imap_folder=excluded.imap_folder,
                rss_urls=excluded.rss_urls,
                default_query=excluded.default_query
        """, settings_data)


def add_or_update_article(
    title: str,
    url: str,
    content: str,
    date: str,
    relevant: bool,
    score: float,
    summary: str,
    key_points: List[str],
    justification: str
) -> int:
    key_points_str = json.dumps(key_points)
    relevant_int = 1 if relevant else 0
    now_str = datetime.now().isoformat()

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO articles (
                title, url, content, date, relevant, score,
                summary, key_points, justification, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title=excluded.title,
                content=excluded.content,
                date=excluded.date,
                relevant=excluded.relevant,
                score=excluded.score,
                summary=excluded.summary,
                key_points=excluded.key_points,
                justification=excluded.justification,
                created_at=excluded.created_at
        """, (title, url, content, date, relevant_int, score, summary, key_points_str, justification, now_str))
        return cursor.lastrowid


def get_articles(
    relevant_only: Optional[bool] = None,
    search_query: Optional[str] = None,
    sort_by: str = "date",  # 'date' or 'score'
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM articles WHERE 1=1"
    params: List[Any] = []

    if relevant_only is not None:
        query += " AND relevant = ?"
        params.append(1 if relevant_only else 0)

    if search_query:
        query += " AND (title LIKE ? OR content LIKE ? OR summary LIKE ?)"
        like_pattern = f"%{search_query}%"
        params.extend([like_pattern, like_pattern, like_pattern])

    if sort_by == "score":
        query += " ORDER BY score DESC, date DESC"
    else:
        query += " ORDER BY date DESC, score DESC"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            try:
                d["key_points"] = json.loads(d["key_points"]) if d["key_points"] else []
            except Exception:
                d["key_points"] = []
            results.append(d)
        return results


def clear_articles():
    with get_connection() as conn:
        conn.execute("DELETE FROM articles")
