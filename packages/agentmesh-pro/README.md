# AgentMesh Pro Framework (`packages/agentmesh-pro`)

Enterprise multi-agent execution framework providing LangGraph state orchestration, LiteLLM multi-provider model gateway with fallback routing, PostgreSQL + PGVector memory storage, Redis session caching, and Langfuse observability integration.

## Features

- **LangGraph State Orchestration**: Stateful graph execution with Human-In-The-Loop (HITL) approval nodes (`MeshOrchestrator`).
- **LiteLLM Gateway**: Multi-provider LLM gateway with automatic failover routing (`ModelGateway`).
- **RAG & Session Storage**: PostgreSQL/PGVector memory store and Redis cache with in-memory fallbacks (`MemoryStore`, `CacheManager`).
- **Observability**: Langfuse tracing integration with local logging fallback (`ObservabilityTracer`).
- **Pydantic Contracts**: Strict input/output contracts (`AgentQueryRequest`, `AgentQueryResponse`, `HumanApprovalDecision`).

## Usage

```python
from agentmesh_pro.orchestrator import MeshOrchestrator
from agentmesh_pro.schemas import AgentQueryRequest

orchestrator = MeshOrchestrator()

request = AgentQueryRequest(
    user_id="user_123",
    session_id="sess_456",
    prompt="Synthesize research brief on market trends",
)

response = await orchestrator.execute_query(request)
print(response.response_text)
```
