# AgentMesh

> **A decentralized coordination mesh for autonomous AI agents.**

AgentMesh is an open-source monorepo for building AI agent applications with a shared infrastructure of **Nostr** coordination, **IPFS** storage, and **LLM** abstraction.

---

## Vision

AgentMesh is infrastructure for digital sovereignty:

- **No Central Servers**: No single point of failure. The system lives on users' nodes.
- **Sovereign Identity**: Every agent and user owns their cryptographic keys (Nostr).
- **Distributed Memory**: Content-addressable storage on IPFS.
- **Agent-to-Agent (A2A) Collaboration**: Open protocols, not proprietary APIs.

---

## Project Structure

The repository is a monorepo managed with [uv](https://docs.astral.sh/uv/):

```
agentmesh/
├── packages/                  # Shared libraries
│   ├── agentmesh-core/        # BaseAgent, MeshConfig, models, logging
│   ├── agentmesh-llm/         # LLM providers (Gemini, OpenAI, Anthropic, Ollama)
│   ├── agentmesh-relay/       # Nostr P2P communication layer
│   ├── agentmesh-vault/       # IPFS content-addressable storage
│   └── agentmesh-studio/      # CLI tools (agentmesh info/vision)
├── apps/                      # Applications
│   ├── newsletter-filter/     # Cognitive newsletter filtering + web UI
│   ├── podcast-generator/     # Newsletter → Italian podcast pipeline
│   ├── econnet/               # ABM economic simulator
│   ├── motedico/              # Decentralized project collaboration mesh
│   ├── erpseed-agent/         # Sovereign ERPSeed low-code & enterprise agent
│   └── agentmesh-pro/         # Enterprise production AI agent execution system
├── scripts/
│   └── new-app.sh             # Scaffolding tool for new apps
├── docs/                      # Technical documentation
└── pyproject.toml             # Workspace root config
```

---

## Quick Start

```bash
# Install all dependencies
uv sync

# Create a new app from the standard template
bash scripts/new-app.sh my-new-app

# Run an app
PYTHONPATH=apps/newsletter-filter uv run python apps/newsletter-filter/main.py --server
PYTHONPATH=apps/podcast-generator uv run python apps/podcast-generator/main.py daily
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --ticks 200 --visualize
PYTHONPATH=apps/motedico uv run python apps/motedico/main.py --server
PYTHONPATH=apps/erpseed-agent uv run python apps/erpseed-agent/main.py --server --port 8000
uv run --package agentmesh-pro python apps/agentmesh-pro/main.py --server --port 8000
```

---

## Creating a New App

Every app follows the standard template. To create one:

```bash
bash scripts/new-app.sh <app-name>          # with web layer (FastAPI + Jinja2)
bash scripts/new-app.sh <sim-name> --no-web  # without web layer
```

This generates the full structure:

```
apps/{app-name}/
├── pyproject.toml           # Dependencies and build config
├── main.py                  # argparse CLI (--server, --port, --host)
├── README.md
├── .env.example
├── .gitignore
├── {app_name}/
│   ├── __init__.py          # __version__
│   ├── config.py            # Pydantic Settings (env vars)
│   ├── agents/              # Agent implementations
│   ├── web/
│   │   ├── app.py           # FastAPI + lifespan manager
│   │   ├── db.py            # SQLite (data/ dir, WAL mode)
│   │   └── templates/       # Jinja2 + Tailwind + HTMX
│   └── data/                # Database files (gitignored)
└── tests/
    ├── conftest.py          # Shared fixtures (temp DB)
    └── test_*.py
```

---

## Applications

| App | Description | Web | CLI |
|-----|-------------|-----|-----|
| **newsletter-filter** | Cognitive newsletter filtering — extracts and scores relevant articles from RSS/IMAP | FastAPI + HTMX | `--server`, `--daemon`, `--source-type` |
| **podcast-generator** | Newsletter → Italian podcast pipeline (TTS, multi-LLM, Nostr + IPFS) | FastAPI + OAuth | `daily`, `weekly`, `fetch-all`, `server` |
| **econnet** | ABM economic simulator with RL consumers, Graeberian modes, and emergent market dynamics | FastAPI + HTMX | `--ticks`, `--consumers`, `--visualize`, `--graeber`, `--server` |
| **motedico** | Decentralized project collaboration and advisory mesh | FastAPI + HTMX | `--server` |
| **erpseed-agent** | Sovereign ERPSeed low-code & enterprise agent (domain sub-agents, IPFS Vault, FatturaPA XML, dynamic SysModel CRUD) | FastAPI + HTMX | `--server`, `--port` |
| **agentmesh-pro** | Enterprise production AI agent execution system (PostgreSQL/PGVector, LangGraph, LiteLLM, Langfuse, Pi Coding Agent) | FastAPI REST | `--server`, `--port` |

---

## Core Packages

| Package | Description |
|---------|-------------|
| **agentmesh-core** | `BaseAgent`, `MeshConfig`, `MeshOrchestrator`, structured logging, metrics |
| **agentmesh-llm** | Unified LLM interface with factory pattern (Gemini, OpenAI, Anthropic, Ollama) |
| **agentmesh-relay** | Nostr protocol integration — `NostrAgent` with event publishing, listening, A2A |
| **agentmesh-vault** | IPFS content-addressable storage — `VaultAgent` with mock and real providers |
| **agentmesh-studio** | CLI tools (`agentmesh info`, `agentmesh vision`) |

---

## Development

```bash
# Run lint
uv run ruff check apps/ packages/

# Run tests for all apps
uv run pytest apps/newsletter-filter/tests -v
uv run pytest apps/podcast-generator/tests -v
uv run pytest apps/econnet/tests -v
uv run pytest apps/motedico/tests -v

# Sync all workspace packages
uv sync --all-packages
```

---

## Documentation

| Document | Content |
|----------|---------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Mesh layers and technical details |
| [docs/VISION.md](docs/VISION.md) | Philosophy and digital sovereignty |
| [docs/A2A_PROTOCOL.md](docs/A2A_PROTOCOL.md) | Agent-to-Agent communication protocol |
| [docs/SECURITY.md](docs/SECURITY.md) | Threat model and mitigations |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Development roadmap |
| [docs/README.md](docs/README.md) | Full documentation index |

---

**AgentMesh: The mesh is the message.**
