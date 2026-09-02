# AgentMesh Pro - Enterprise Production AI Agent System

AgentMesh Pro evolves AgentMesh into a production-grade multi-agent execution platform with:

1. **FastAPI Web API Layer**: Async-first endpoints and strict Pydantic contract validation.
2. **Persistence & Caching**: PostgreSQL + PGVector for long-term RAG memory and Redis for state session caching.
3. **Advanced Orchestration**: LangGraph integration with feedback loops and human-in-the-loop approvals.
4. **Resilient Gateway & Observability**: LiteLLM multi-provider fallback and Langfuse tracing.
5. **Pi Coding Agent**: Integration for self-healing code, auto-generated unit tests, and continuous dev automation.

## Running the Server

```bash
uv run --package agentmesh-pro python apps/agentmesh-pro/main.py --server --port 8000
```
