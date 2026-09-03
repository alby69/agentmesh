"""Tests for orchestrator in AgentMesh Pro."""

import pytest
from agentmesh_pro.schemas import AgentQueryRequest
from agentmesh_pro.orchestrator import MeshOrchestrator


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
