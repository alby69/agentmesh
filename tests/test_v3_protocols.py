import pytest
from unittest.mock import MagicMock, AsyncMock
from agentmesh.relay.agent import NostrAgent
from agentmesh.core import MeshConfig
from agentmesh.core.models import AgentMessage

@pytest.mark.asyncio
async def test_nostr_agent_rate_limiting():
    config = MeshConfig()
    # Mock the Client to avoid real network calls
    with MagicMock() as mock_client:
        # We need to bypass the Client(self.keys) in __init__ or mock it
        # Since we're just testing the logic of _is_rate_limited
        agent = NostrAgent(config)
        agent.client = mock_client

        pubkey = "test_pubkey"

        # Send many messages quickly
        for i in range(10):
            assert agent._is_rate_limited(pubkey) is False

        # The 11th message should be rate limited
        assert agent._is_rate_limited(pubkey) is True

@pytest.mark.asyncio
async def test_agent_message_parsing():
    config = MeshConfig()
    agent = NostrAgent(config)
    agent.handle_message = AsyncMock()

    # Mock event
    mock_event = MagicMock()
    mock_event.kind.return_value = 29001 # KIND_AGENT_MESSAGE
    mock_event.author().to_hex.return_value = "sender_pubkey"

    msg_json = '{"sender": "sender_pubkey", "type": "task", "payload": {"action": "test"}}'
    mock_event.content.return_value = msg_json

    await agent._process_incoming_event(mock_event)

    agent.handle_message.assert_called_once()
    parsed_msg = agent.handle_message.call_args[0][0]
    assert parsed_msg.sender == "sender_pubkey"
    assert parsed_msg.payload["action"] == "test"
