# AgentMesh Pro Server (`apps/agentmesh-pro-server`)

FastAPI web API server and CLI wrapper application for `agentmesh-pro`.

## Quick Start

```bash
# 1. Install dependencies
uv sync --package agentmesh-pro-server

# 2. Copy environment template
cp apps/agentmesh-pro-server/.env.example apps/agentmesh-pro-server/.env

# 3. Start the REST API server
uv run --package agentmesh-pro-server python apps/agentmesh-pro-server/main.py --server --port 8000
```

## Endpoints

- `GET /health` - Service status and subsystem health check
- `POST /api/v1/query` - Execute query through LangGraph multi-agent orchestrator
- `POST /api/v1/approval` - Submit human approval decision for gated workflow tasks
