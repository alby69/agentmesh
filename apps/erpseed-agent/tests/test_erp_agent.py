"""Unit tests for ERPSeedAgent, TenantResolver, ERPSeedBridge, CapabilitySync, and ERPSeedPolicyAgent."""

import pytest
import httpx
from agentmesh.core import AgentMessage

from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.erp_agent import ERPSeedAgent
from erpseed_agent.agents.policy_agent import ERPSeedPolicyAgent
from erpseed_agent.bridge.tenant_resolver import TenantResolver
from erpseed_agent.bridge.executor import ERPSeedBridge
from erpseed_agent.bridge.capability_sync import CapabilitySync
from erpseed_agent.web.db import init_db, list_cached_capabilities


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


@pytest.mark.asyncio
async def test_tenant_resolver():
    resolver = TenantResolver(default_tenant_id=1, strict_mode=False)

    # 1. Fallback to default tenant
    res = await resolver.resolve("npub1unknown")
    assert res["tenant_id"] == 1

    # 2. Register mapping
    resolver.register_tenant("npub1alice", tenant_id=42, api_key="secret_token")
    res_alice = await resolver.resolve("npub1alice")
    assert res_alice["tenant_id"] == 42
    assert res_alice["api_key"] == "secret_token"

    # 3. Strict mode error
    strict_resolver = TenantResolver(strict_mode=True)
    with pytest.raises(ValueError, match="No tenant mapping registered"):
        await strict_resolver.resolve("npub1unknown")


@pytest.mark.asyncio
async def test_erpseed_bridge_execution():
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        elif request.url.path == "/api/v1/ai/execute":
            return httpx.Response(200, json={"status": "success", "order_id": 101, "order_number": "SO-001"})
        elif request.url.path == "/api/v1/ai/builder":
            return httpx.Response(200, json={"status": "success", "module": "fleet_management"})
        return httpx.Response(404, json={"error": "not found"})

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport)
    bridge = ERPSeedBridge(base_url="http://mock-erpseed", client=client)

    # Health check
    assert await bridge.health_check() is True

    # Execute domain command
    result = await bridge.execute(
        action="sales.create_order",
        params={"customer_id": 1, "lines": []},
        tenant_id=5,
    )
    assert result["status"] == "success"
    assert result["order_id"] == 101

    # Execute builder command
    builder_res = await bridge.execute(
        action="builder.generate_module",
        params={"user_request": "Create fleet model"},
        tenant_id=5,
    )
    assert builder_res["module"] == "fleet_management"

    await bridge.close()


@pytest.mark.asyncio
async def test_capability_sync():
    mock_manifest = {
        "manifest": [
            {
                "agent": "sales",
                "capabilities": [
                    {
                        "name": "sales.create_order",
                        "description": "Creates a sales order",
                        "parameters": {"type": "object"},
                    }
                ],
            }
        ]
    }

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/ai/capabilities":
            return httpx.Response(200, json=mock_manifest)
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport)
    cap_sync = CapabilitySync(
        base_url="http://mock-erpseed",
        agent_id="test-agent",
        public_key="test-key",
        client=client,
    )

    caps = await cap_sync.fetch_and_translate()
    assert len(caps) == 1
    assert caps[0].name == "sales.create_order"
    assert caps[0].agent_id == "test-agent"

    # Verify SQLite caching
    cached = list_cached_capabilities()
    assert len(cached) == 1
    assert cached[0]["name"] == "sales.create_order"

    await cap_sync.close()


@pytest.mark.asyncio
async def test_erpseed_agent_handle_message():
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        elif request.url.path == "/api/v1/ai/capabilities":
            return httpx.Response(200, json={"manifest": []})
        elif request.url.path == "/api/v1/ai/execute":
            return httpx.Response(200, json={"invoice_number": "INV-2026-01"})
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport)

    config = ERPSeedConfig(agent_id="erp-test-agent")
    bridge = ERPSeedBridge(base_url="http://mock-erpseed", client=client)
    cap_sync = CapabilitySync(base_url="http://mock-erpseed", client=client)
    resolver = TenantResolver(default_tenant_id=7)

    agent = ERPSeedAgent(
        config=config,
        bridge=bridge,
        tenant_resolver=resolver,
        capability_sync=cap_sync,
    )
    await agent.start()

    # 1. Non-task message
    info_msg = AgentMessage(sender="pubkey_1", message_type="info", payload={})
    reply_info = await agent.handle_message(info_msg)
    assert reply_info.message_type == "info"
    assert reply_info.payload["status"] == "ignored"

    # 2. Task message missing action
    invalid_task = AgentMessage(sender="pubkey_1", message_type="task", payload={})
    reply_err = await agent.handle_message(invalid_task)
    assert reply_err.message_type == "error"
    assert "Missing 'action'" in reply_err.payload["reason"]

    # 3. Valid task message execution
    valid_task = AgentMessage(
        sender="pubkey_1",
        message_type="task",
        payload={
            "action": "purchases.create_invoice",
            "params": {"vendor_id": 10},
        },
    )
    reply_ok = await agent.handle_message(valid_task)
    assert reply_ok.message_type == "response"
    assert reply_ok.payload["status"] == "success"
    assert reply_ok.payload["tenant_id"] == 7
    assert reply_ok.payload["result"]["invoice_number"] == "INV-2026-01"

    await agent.stop()


@pytest.mark.asyncio
async def test_policy_agent():
    config = ERPSeedConfig(agent_id="erp-test-agent")
    bridge = ERPSeedBridge(base_url="http://mock-erpseed")
    agent = ERPSeedAgent(config=config, bridge=bridge)

    policy_agent = ERPSeedPolicyAgent(
        target_agent=agent,
        allowed_actions={"sales.*", "purchases.*"},
        blocked_actions={"sales.delete_all"},
    )

    # Allowed
    assert policy_agent.is_action_allowed("sales.create_order") is True
    assert policy_agent.is_action_allowed("purchases.create_invoice") is True

    # Blocked
    assert policy_agent.is_action_allowed("sales.delete_all") is False
    assert policy_agent.is_action_allowed("builder.generate_module") is False

    # Test blocked task message handling
    blocked_task = AgentMessage(
        sender="pubkey_1",
        message_type="task",
        payload={"action": "builder.generate_module"},
    )
    reply = await policy_agent.handle_message(blocked_task)
    assert reply.message_type == "error"
    assert reply.payload["status"] == "blocked"
