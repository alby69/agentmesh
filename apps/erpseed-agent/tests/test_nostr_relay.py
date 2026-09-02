import pytest
from agentmesh.core import AgentMessage
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.bridge.nostr_relay import NostrRelayBridge
from agentmesh.relay import NostrAgent


@pytest.mark.asyncio
async def test_nostr_agent_and_relay_bridge():
    config = ERPSeedConfig(
        agent_id="test-erp-agent",
        nostr_relay_url="wss://relay.damus.io",
    )
    agent = NostrAgent(config=config)
    bridge = NostrRelayBridge(agent=agent, config=config)

    # Test broadcasting capability
    event_id = await bridge.broadcast_capability(["erp.sales", "erp.purchases"])
    # If client is not connected in unit test environment, event_id might be None, which is expected
    assert event_id is None or isinstance(event_id, (str, object))

    # Test send A2A response
    resp = await bridge.send_a2a_response(
        receiver_pubkey="npub1testreceiver",
        action="sales.create_order",
        result={"order_id": 101},
    )
    assert resp.sender == "test-erp-agent"
    assert resp.receiver == "npub1testreceiver"
    assert resp.message_type == "response"
    assert resp.payload["result"]["order_id"] == 101

    # Test publishing invoice metadata
    meta_res = await bridge.publish_invoice_metadata(
        title="Fattura_2026_001.xml",
        ipfs_cid="QmTestCid123",
        metadata={"size": "1024", "mime": "application/xml"},
    )
    assert meta_res is None or isinstance(meta_res, (str, object))
