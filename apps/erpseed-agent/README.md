# erpseed-agent

ERPSeed Builder Agent for AgentMesh — Enterprise Resource Planning operations, fiscal compliance, and dynamic low-code ERP integration.

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
│   │   ├── erp_agent.py                 # ERPSeedAgent (BaseAgent)
│   │   └── policy_agent.py              # ERPSeedPolicyAgent
│   ├── bridge/
│   │   ├── executor.py                  # ERPSeedBridge HTTP REST client
│   │   ├── tenant_resolver.py           # npub -> tenant_id mapping
│   │   ├── capability_sync.py           # /api/v1/ai/capabilities manifest sync
│   │   └── event_publisher.py           # ERPSEED domain event bridge
│   └── web/
│       ├── app.py                       # FastAPI server + routes
│       ├── db.py                        # SQLite database layer
│       └── templates/                   # Jinja2 + Tailwind + HTMX
└── tests/
    ├── conftest.py                      # Shared fixtures
    ├── test_erp_agent.py                # Agent & bridge tests
    └── test_web.py                      # Web route tests
```
