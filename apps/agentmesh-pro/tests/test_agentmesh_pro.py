"""Unit and integration tests for AgentMesh Pro."""

import pytest
from fastapi.testclient import TestClient

from agentmesh_pro.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
)
from agentmesh_pro.persistence import CacheManager, MemoryStore
from agentmesh_pro.gateway import ModelGateway
from agentmesh_pro.orchestrator import MeshOrchestrator
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "postgres_pgvector" in data["services"]
    assert "redis_cache" in data["services"]


def test_pydantic_schemas():
    req = AgentQueryRequest(
        user_id="user_123",
        session_id="sess_456",
        prompt="Test query for agentmesh",
    )
    assert req.user_id == "user_123"
    assert req.require_human_approval is False

    res = AgentQueryResponse(
        session_id="sess_456",
        status="completed",
        response_text="Test response",
    )
    assert res.status == "completed"


def test_cache_and_memory_fallback():
    cache = CacheManager(redis_url="redis://nonexistent:6379/0")
    cache.set("key1", "val1")
    assert cache.get("key1") == "val1"
    cache.delete("key1")
    assert cache.get("key1") is None

    store = MemoryStore()
    stored = store.store_memory("sess_1", "k1", "Sample content for testing memory")
    assert stored is True
    results = store.search_memory("sess_1", "Sample")
    assert len(results) >= 1
    assert results[0]["key"] == "k1"


@pytest.mark.asyncio
async def test_model_gateway_fallback():
    gateway = ModelGateway(default_model="invalid/primary", fallback_model="invalid/fallback")
    res = await gateway.generate_response([{"role": "user", "content": "Hello"}])
    assert "content" in res
    assert res["status"] in ["fallback_success", "simulated_success"]


@pytest.mark.asyncio
async def test_orchestrator_execution():
    orchestrator = MeshOrchestrator()
    req = AgentQueryRequest(
        user_id="user_test",
        session_id="sess_test_100",
        prompt="Analyze market trends",
    )
    res = await orchestrator.execute_query(req)
    assert res.session_id == "sess_test_100"
    assert res.response_text != ""
    assert len(res.steps) >= 1


def test_api_query_and_approval_endpoints(client):
    # Test query endpoint
    payload = {
        "user_id": "api_user",
        "session_id": "api_sess_1",
        "prompt": "Summarize latest news",
        "require_human_approval": False,
    }
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "api_sess_1"
    assert data["response_text"] != ""

    # Test approval endpoint
    approval_payload = {
        "task_id": "task_999",
        "approved": True,
        "feedback": "Approved by supervisor",
    }
    appr_response = client.post("/api/v1/approval", json=approval_payload)
    assert appr_response.status_code == 200
    appr_data = appr_response.json()
    assert appr_data["session_id"] == "task_999"
    assert appr_data["status"] == "approved_and_executed"
