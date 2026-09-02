"""SQLite database layer for erpseed-agent with invoice, workflow, and vault persistent storage."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

_APP_DIR = Path(__file__).resolve().parent.parent.parent
_default_db = str(_APP_DIR / "data" / "erpseed_agent.db")
DB_PATH = os.getenv("ERPSEED_AGENT_DB_PATH", _default_db)


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
            CREATE TABLE IF NOT EXISTS tenant_mappings (
                npub TEXT PRIMARY KEY,
                tenant_id INTEGER NOT NULL,
                api_key TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS capability_cache (
                name TEXT PRIMARY KEY,
                description TEXT DEFAULT '',
                category TEXT DEFAULT '',
                input_schema TEXT DEFAULT '{}',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                sender TEXT,
                action TEXT,
                status TEXT,
                details TEXT DEFAULT '',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                ipfs_cid TEXT,
                ipfs_url TEXT,
                xml_content TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                trigger_event TEXT,
                action TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vault_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                ipfs_cid TEXT UNIQUE,
                file_type TEXT DEFAULT 'document',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# Database helper functions

def set_tenant_mapping(npub: str, tenant_id: int, api_key: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tenant_mappings (npub, tenant_id, api_key)
            VALUES (?, ?, ?)
            ON CONFLICT(npub) DO UPDATE SET
                tenant_id = excluded.tenant_id,
                api_key = excluded.api_key
            """,
            (npub, tenant_id, api_key),
        )


def get_tenant_mapping(npub: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT npub, tenant_id, api_key, created_at FROM tenant_mappings WHERE npub = ?",
            (npub,),
        ).fetchone()
        if row:
            return dict(row)
        return None


def list_tenant_mappings() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT npub, tenant_id, api_key, created_at FROM tenant_mappings ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_tenant_mapping(npub: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM tenant_mappings WHERE npub = ?", (npub,))


def update_capability_cache(capabilities: List[Dict[str, Any]]) -> None:
    with get_connection() as conn:
        for cap in capabilities:
            conn.execute(
                """
                INSERT INTO capability_cache (name, description, category, input_schema, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET
                    description = excluded.description,
                    category = excluded.category,
                    input_schema = excluded.input_schema,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    cap.get("name", ""),
                    cap.get("description", ""),
                    cap.get("category", ""),
                    json.dumps(cap.get("input_schema", cap.get("parameters", {}))),
                ),
            )


def list_cached_capabilities() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name, description, category, input_schema, updated_at FROM capability_cache ORDER BY name"
        ).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["input_schema"] = json.loads(d.get("input_schema", "{}"))
            except Exception:
                d["input_schema"] = {}
            results.append(d)
        return results


def log_agent_action(message_id: str, sender: str, action: str, status: str, details: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO agent_logs (message_id, sender, action, status, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, sender, action, status, details),
        )


def list_agent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, message_id, sender, action, status, details, timestamp FROM agent_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def save_invoice(invoice_number: str, ipfs_cid: str, ipfs_url: str, xml_content: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO invoices (invoice_number, ipfs_cid, ipfs_url, xml_content)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(invoice_number) DO UPDATE SET
                ipfs_cid = excluded.ipfs_cid,
                ipfs_url = excluded.ipfs_url,
                xml_content = excluded.xml_content
            """,
            (invoice_number, ipfs_cid, ipfs_url, xml_content),
        )


def list_invoices(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, invoice_number, ipfs_cid, ipfs_url, created_at FROM invoices ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def save_workflow(name: str, trigger_event: str, action: str, status: str = "active") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO workflows (name, trigger_event, action, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                trigger_event = excluded.trigger_event,
                action = excluded.action,
                status = excluded.status
            """,
            (name, trigger_event, action, status),
        )


def list_workflows() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, trigger_event, action, status, created_at FROM workflows ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def save_vault_file(title: str, ipfs_cid: str, file_type: str = "document") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO vault_files (title, ipfs_cid, file_type)
            VALUES (?, ?, ?)
            ON CONFLICT(ipfs_cid) DO UPDATE SET
                title = excluded.title,
                file_type = excluded.file_type
            """,
            (title, ipfs_cid, file_type),
        )


def list_vault_files() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, ipfs_cid, file_type, created_at FROM vault_files ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]
