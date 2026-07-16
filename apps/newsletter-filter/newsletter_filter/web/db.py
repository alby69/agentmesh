import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("newsletter_filter.web.db")

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "newsletter_filter.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            date TEXT,
            content TEXT,
            relevant INTEGER DEFAULT 0,
            score REAL DEFAULT 0.0,
            summary TEXT,
            key_points TEXT,
            justification TEXT,
            source_type TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS scan_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source TEXT NOT NULL,
            query TEXT,
            status TEXT DEFAULT 'pending',
            total_articles INTEGER DEFAULT 0,
            relevant_articles INTEGER DEFAULT 0,
            started_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT
        );
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)


def save_article(article: Dict[str, Any], db_path: Optional[Path] = None) -> bool:
    conn = get_connection(db_path)
    try:
        analysis = article.get("analysis", {})
        conn.execute("""
            INSERT OR REPLACE INTO articles
            (title, url, date, content, relevant, score, summary, key_points, justification, source_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.get("title", ""),
            article.get("url", ""),
            article.get("date", ""),
            article.get("content", ""),
            1 if analysis.get("relevant") else 0,
            analysis.get("score", 0.0),
            analysis.get("summary", ""),
            json.dumps(analysis.get("key_points", []), ensure_ascii=False),
            analysis.get("justification", ""),
            article.get("source_type", ""),
        ))
        conn.commit()
        return True
    except Exception as e:
        logger.error("Error saving article: %s", e)
        return False
    finally:
        conn.close()


def get_articles(
    relevant_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    query = "SELECT * FROM articles"
    if relevant_only:
        query += " WHERE relevant = 1"
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"

    rows = conn.execute(query, (limit, offset)).fetchall()
    conn.close()

    articles = []
    for row in rows:
        a = dict(row)
        a["key_points"] = json.loads(a.get("key_points") or "[]")
        a["relevant"] = bool(a.get("relevant"))
        articles.append(a)
    return articles


def get_article_count(relevant_only: bool = False, db_path: Optional[Path] = None) -> int:
    conn = get_connection(db_path)
    if relevant_only:
        row = conn.execute("SELECT COUNT(*) FROM articles WHERE relevant = 1").fetchone()
    else:
        row = conn.execute("SELECT COUNT(*) FROM articles").fetchone()
    conn.close()
    return row[0] if row else 0


def clear_articles(db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    conn.execute("DELETE FROM articles")
    conn.commit()
    conn.close()


def get_db_settings(db_path: Optional[Path] = None) -> Dict[str, str]:
    conn = get_connection(db_path)
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}


def save_db_settings(settings: Dict[str, str], db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    for key, value in settings.items():
        conn.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        """, (key, value))
    conn.commit()
    conn.close()


def save_scan_job(
    source_type: str,
    source: str,
    query: str,
    db_path: Optional[Path] = None,
) -> int:
    conn = get_connection(db_path)
    cursor = conn.execute("""
        INSERT INTO scan_jobs (source_type, source, query, status)
        VALUES (?, ?, ?, 'running')
    """, (source_type, source, query))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id


def complete_scan_job(
    job_id: int,
    total: int,
    relevant: int,
    db_path: Optional[Path] = None,
) -> None:
    conn = get_connection(db_path)
    conn.execute("""
        UPDATE scan_jobs
        SET status = 'completed', total_articles = ?, relevant_articles = ?, completed_at = datetime('now')
        WHERE id = ?
    """, (total, relevant, job_id))
    conn.commit()
    conn.close()


def get_scan_jobs(limit: int = 10, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM scan_jobs ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
