# erpseed-agent

DESCRIPTION_PLACEHOLDER

## Quick Start

```bash
# 1. Installa le dipendenze
uv sync --package erpseed-agent

# 2. Configura
cp apps/erpseed-agent/.env.example apps/erpseed-agent/.env

# 3. Avvia la Web UI
PYTHONPATH=apps/erpseed-agent uv run python apps/erpseed-agent/main.py --server --port 8000
```

## Struttura

```
apps/erpseed-agent/
├── main.py                              # CLI entry point
├── pyproject.toml                       # Dipendenze e configurazione build
├── .env.example                         # Template configurazione
├── erpseed_agent/
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
