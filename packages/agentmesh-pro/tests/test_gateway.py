"""Tests for model gateway in AgentMesh Pro."""

import pytest
from agentmesh_pro.gateway import ModelGateway


@pytest.mark.asyncio
async def test_model_gateway_fallback():
    gateway = ModelGateway(default_model="invalid/primary", fallback_model="invalid/fallback")
    res = await gateway.generate_response([{"role": "user", "content": "Hello"}])
    assert "content" in res
    assert res["status"] in ["fallback_success", "simulated_success"]
