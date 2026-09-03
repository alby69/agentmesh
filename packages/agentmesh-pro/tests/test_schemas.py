"""Tests for AgentMesh Pro contract schemas."""

from agentmesh_pro.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    HumanApprovalDecision,
    HealthCheckResponse,
)


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

    approval = HumanApprovalDecision(
        task_id="task_001",
        approved=True,
        feedback="Looks good",
    )
    assert approval.task_id == "task_001"
    assert approval.approved is True

    health = HealthCheckResponse(
        status="ok",
        version="0.1.0",
        services={"redis": "connected"},
    )
    assert health.status == "ok"
