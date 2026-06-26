import pytest
from agentmesh.core.models import AgentCapability, AgentMessage
from agentmesh.core import MeshConfig, MeshOrchestrator

def test_capability_serialization():
    cap = AgentCapability(
        agent_id="test-id",
        name="Test Agent",
        description="A test agent",
        version="1.0.0",
        public_key="npub1...",
        capabilities=["test", "demo"]
    )
    json_data = cap.model_dump_json()
    assert '"agent_id":"test-id"' in json_data
    assert '"capabilities":["test","demo"]' in json_data

def test_message_serialization():
    msg = AgentMessage(
        sender="npub1-sender",
        receiver="npub1-receiver",
        message_type="task",
        payload={"action": "test"}
    )
    json_data = msg.model_dump_json(by_alias=True)
    assert '"sender":"npub1-sender"' in json_data
    assert '"type":"task"' in json_data

@pytest.mark.asyncio
async def test_orchestrator_capability_gen():
    config = MeshConfig(agent_id="orch-test", agent_name="Orchestrator")
    orch = MeshOrchestrator(config)

    class MockAgent:
        def __init__(self):
            self.capabilities = ["mock"]
        async def start(self): pass
        async def stop(self): pass

    orch.register_agent("mock", MockAgent())
    cap = orch.get_agent_capability("mock", "test-pk")

    assert cap.agent_id == "orch-test"
    assert cap.capabilities == ["mock"]
    assert cap.public_key == "test-pk"
