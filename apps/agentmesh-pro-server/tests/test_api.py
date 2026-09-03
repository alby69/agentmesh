"""Integration tests for AgentMesh Pro REST API Server."""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

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


def test_api_query_endpoint(client):
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


def test_api_approval_endpoint(client):
    approval_payload = {
        "task_id": "task_999",
        "approved": True,
        "feedback": "Approved by supervisor",
    }
    response = client.post("/api/v1/approval", json=approval_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "task_999"
    assert data["status"] == "approved_and_executed"
