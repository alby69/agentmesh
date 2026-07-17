#!/usr/bin/env bash
#
# new-app.sh — scaffolds a new AgentMesh app with the standard template.
#
# Usage:  bash scripts/new-app.sh <app-name> [--no-web]
#
# Example:
#   bash scripts/new-app.sh my-tool
#   bash scripts/new-app.sh my-sim --no-web
#
set -euo pipefail

# ── Args ────────────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <app-name> [--no-web]"
  exit 1
fi

APP_NAME="$1"
NO_WEB="${2:-}"

# Validate name (kebab-case)
if [[ ! "$APP_NAME" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
  echo "Error: app name must be kebab-case (e.g. my-cool-app)"
  exit 1
fi

# Convert kebab-case to snake_case for Python package
PKG_NAME="${APP_NAME//-/_}"

APP_DIR="apps/${APP_NAME}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -d "$REPO_ROOT/$APP_DIR" ]]; then
  echo "Error: $APP_DIR already exists"
  exit 1
fi

echo "Creating app: ${APP_NAME} (package: ${PKG_NAME})"

# ── Create directories ─────────────────────────────────────────────────
mkdir -p "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/templates"
mkdir -p "$REPO_ROOT/$APP_DIR/${PKG_NAME}/agents"
mkdir -p "$REPO_ROOT/$APP_DIR/tests"
mkdir -p "$REPO_ROOT/$APP_DIR/data"

# ── pyproject.toml ─────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/pyproject.toml" << 'PYPROJECT'
[project]
name = "APP_NAME_PLACEHOLDER"
version = "0.1.0"
description = "DESCRIPTION_PLACEHOLDER"
requires-python = ">=3.10"
dependencies = [
    "agentmesh-core",
    "agentmesh-llm",
    "agentmesh-relay",
    "agentmesh-vault",
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.9",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.1.0",
]

[tool.uv.sources]
agentmesh-core = { workspace = true }
agentmesh-llm = { workspace = true }
agentmesh-relay = { workspace = true }
agentmesh-vault = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
PYPROJECT

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/pyproject.toml"

# ── main.py ────────────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/main.py" << 'MAIN'
"""CLI entry point for APP_NAME_PLACEHOLDER."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="APP_NAME_PLACEHOLDER",
        description="DESCRIPTION_PLACEHOLDER",
    )
    parser.add_argument(
        "--server", action="store_true",
        help="Start the web UI server",
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Port for the web server (default: 8000)",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0",
        help="Host for the web server (default: 0.0.0.0)",
    )
    return parser


async def run_server(host: str, port: int) -> None:
    import uvicorn
    from PKG_NAME_PLACEHOLDER.web.app import app

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.server:
        asyncio.run(run_server(args.host, args.port))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
MAIN

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/main.py"
sed -i "s/PKG_NAME_PLACEHOLDER/${PKG_NAME}/g" "$REPO_ROOT/$APP_DIR/main.py"

# ── PKG/__init__.py ────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/__init__.py" << 'INIT'
"""APP_NAME_PLACEHOLDER — DESCRIPTION_PLACEHOLDER."""

__version__ = "0.1.0"
INIT

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/__init__.py"

# ── PKG/config.py ──────────────────────────────────────────────────────
ENV_PREFIX="${PKG_NAME^^}"  # e.g. MY_TOOL

cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/config.py" << 'CONFIG'
"""Pydantic Settings for APP_NAME_PLACEHOLDER."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ENV_PREFIX_PLACEHOLDER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: str = Field(default="gemini", description="LLM provider name")

    # Web
    web_host: str = Field(default="0.0.0.0")
    web_port: int = Field(default=8000)

    # App-specific fields go here


def get_settings() -> AppSettings:
    return AppSettings()
CONFIG

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/config.py"
sed -i "s/ENV_PREFIX_PLACEHOLDER/${ENV_PREFIX}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/config.py"

# ── PKG/web/__init__.py ────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/__init__.py" << 'EOF'
EOF

# ── PKG/web/app.py ─────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/app.py" << 'APP'
"""FastAPI web application for APP_NAME_PLACEHOLDER."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from PKG_NAME_PLACEHOLDER.config import get_settings

templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="APP_NAME_PLACEHOLDER",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "index.html", {"config": _settings}
    )
APP

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/app.py"
sed -i "s/PKG_NAME_PLACEHOLDER/${PKG_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/app.py"

# ── PKG/web/db.py ──────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/db.py" << 'DB'
"""SQLite database layer for APP_NAME_PLACEHOLDER."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

_APP_DIR = Path(__file__).resolve().parent.parent.parent
_default_db = str(_APP_DIR / "data" / "${PKG_NAME}.db")
DB_PATH = os.getenv("APP_NAME_UPPER_DB_PATH", _default_db)


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
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                data TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
DB

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/db.py"
sed -i "s/PKG_NAME_PLACEHOLDER/${PKG_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/db.py"
sed -i "s/APP_NAME_UPPER/${ENV_PREFIX}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/db.py"

# ── PKG/web/templates/base.html ───────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/templates/base.html" << 'HTML'
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}APP_NAME_PLACEHOLDER{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 py-3 flex items-center gap-6">
            <a href="/" class="text-lg font-bold text-blue-600">APP_NAME_PLACEHOLDER</a>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-6">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
HTML

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/templates/base.html"

# ── PKG/web/templates/index.html ──────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/templates/index.html" << 'HTML'
{% extends "base.html" %}
{% block title %}APP_NAME_PLACEHOLDER — Home{% endblock %}
{% block content %}
<div class="bg-white rounded-lg shadow-sm p-6">
    <h1 class="text-2xl font-bold mb-4">APP_NAME_PLACEHOLDER</h1>
    <p class="text-gray-600">Benvenuto. Configura le impostazioni e avvia il tuo task.</p>
</div>
{% endblock %}
HTML

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web/templates/index.html"

# ── PKG/agents/__init__.py ────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/${PKG_NAME}/agents/__init__.py" << 'EOF'
EOF

# ── tests/__init__.py ──────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/tests/__init__.py" << 'EOF'
EOF

# ── tests/conftest.py ──────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/tests/conftest.py" << 'CONFTEST'
"""Shared test fixtures for APP_NAME_PLACEHOLDER."""

import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _test_env(tmp_path):
    """Set a temp DB for every test and clean up after."""
    db_path = str(tmp_path / "test.db")
    os.environ["APP_NAME_UPPER_DB_PATH"] = db_path
    yield
    os.environ.pop("APP_NAME_UPPER_DB_PATH", None)
CONFTEST

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/tests/conftest.py"
sed -i "s/APP_NAME_UPPER/${ENV_PREFIX}/g" "$REPO_ROOT/$APP_DIR/tests/conftest.py"

# ── tests/test_web.py ──────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/tests/test_web.py" << 'TEST'
"""Web route tests for APP_NAME_PLACEHOLDER."""

import pytest
from fastapi.testclient import TestClient

from PKG_NAME_PLACEHOLDER.web.app import app
from PKG_NAME_PLACEHOLDER.web.db import init_db


@pytest.fixture(name="client")
def client_fixture():
    init_db()
    return TestClient(app)


def test_index(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "APP_NAME_PLACEHOLDER" in response.text
TEST

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/tests/test_web.py"
sed -i "s/PKG_NAME_PLACEHOLDER/${PKG_NAME}/g" "$REPO_ROOT/$APP_DIR/tests/test_web.py"

# ── .env.example ───────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/.env.example" << 'ENV'
# LLM
${ENV_PREFIX}_LLM_PROVIDER=gemini

# Web
${ENV_PREFIX}_WEB_HOST=0.0.0.0
${ENV_PREFIX}_WEB_PORT=8000
ENV

# ── .gitignore (app-local) ────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/.gitignore" << 'GI'
data/
*.db
*.db-shm
*.db-wal
.env
output/
GI

# ── README.md ──────────────────────────────────────────────────────────
cat > "$REPO_ROOT/$APP_DIR/README.md" << 'README'
# APP_NAME_PLACEHOLDER

DESCRIPTION_PLACEHOLDER

## Quick Start

```bash
# 1. Installa le dipendenze
uv sync --package APP_NAME_PLACEHOLDER

# 2. Configura
cp apps/APP_NAME_PLACEHOLDER/.env.example apps/APP_NAME_PLACEHOLDER/.env

# 3. Avvia la Web UI
PYTHONPATH=apps/APP_NAME_PLACEHOLDER uv run python apps/APP_NAME_PLACEHOLDER/main.py --server --port 8000
```

## Struttura

```
apps/APP_NAME_PLACEHOLDER/
├── main.py                              # CLI entry point
├── pyproject.toml                       # Dipendenze e configurazione build
├── .env.example                         # Template configurazione
├── PKG_NAME_PLACEHOLDER/
│   ├── __init__.py
│   ├── config.py                        # Pydantic Settings (env vars)
│   ├── agents/
│   │   └── __init__.py
│   └── web/
│       ├── __init__.py
│       ├── app.py                       # FastAPI server + routes
│       ├── db.py                        # SQLite database layer
│       └── templates/                   # Jinja2 + Tailwind + HTMX
└── tests/
    ├── conftest.py                      # Shared fixtures
    └── test_web.py                      # Web route tests
```
README

sed -i "s/APP_NAME_PLACEHOLDER/${APP_NAME}/g" "$REPO_ROOT/$APP_DIR/README.md"
sed -i "s/PKG_NAME_PLACEHOLDER/${PKG_NAME}/g" "$REPO_ROOT/$APP_DIR/README.md"

# ── Remove --no-web scaffolding artifacts if requested ─────────────────
if [[ "$NO_WEB" == "--no-web" ]]; then
    rm -rf "$REPO_ROOT/$APP_DIR/${PKG_NAME}/web"
    rm -rf "$REPO_ROOT/$APP_DIR/tests/test_web.py"
fi

echo ""
echo "App created: ${APP_DIR}/"
echo ""
echo "Next steps:"
echo "  1. cd ${APP_DIR}"
echo "  2. uv sync --package ${APP_NAME}"
echo "  3. PYTHONPATH=${APP_DIR} uv run python ${APP_DIR}/main.py --help"
echo ""
