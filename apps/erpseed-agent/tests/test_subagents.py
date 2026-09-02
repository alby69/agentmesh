import pytest
from agentmesh.core import AgentMessage
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.erp_agent import ERPSeedAgent
from erpseed_agent.agents.sales_agent import SalesAgent
from erpseed_agent.agents.inventory_agent import InventoryAgent
from erpseed_agent.agents.hr_agent import HRAgent
from erpseed_agent.agents.fe_agent import FEAgent


class MockBridge:
    async def health_check(self):
        return True

    async def execute(self, action, params, tenant_id=1, api_key=""):
        return {"action": action, "executed": True, "tenant_id": tenant_id, "params": params}

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_subagent_capabilities():
    config = ERPSeedConfig()
    mock_bridge = MockBridge()

    sales = SalesAgent(config=config, bridge=mock_bridge)
    assert await sales.can_handle("sales.create_order")
    order_res = await sales.create_sales_order(customer_id=10, items=[])
    assert order_res["executed"] is True

    inv = InventoryAgent(config=config, bridge=mock_bridge)
    assert await inv.can_handle("inventory.move_stock")
    stock_res = await inv.move_stock(product_id=5, quantity=2.0, source_loc="A", target_loc="B")
    assert stock_res["executed"] is True

    hr = HRAgent(config=config, bridge=mock_bridge)
    assert await hr.can_handle("hr.log_attendance")

    fe = FEAgent(config=config, bridge=mock_bridge)
    xml_res = await fe.generate_fattura_xml(
        invoice_number="INV-2026-001",
        invoice_date="2026-09-02",
        supplier={"name": "Supplier SPA", "vat_id": "01234567890"},
        customer={"name": "Client SRL", "sdi_code": "M5UXCR1"},
        lines=[{"description": "Consulenza IT", "quantity": 10, "unit_price": 50.0}],
    )
    assert xml_res["status"] == "generated"
    assert xml_res["ipfs_cid"].startswith("Qm")


@pytest.mark.asyncio
async def test_main_agent_subagent_routing():
    config = ERPSeedConfig()
    mock_bridge = MockBridge()
    agent = ERPSeedAgent(config=config, bridge=mock_bridge)

    # 1. Route to Sales Agent
    msg_sales = AgentMessage(
        sender="npub1salesuser",
        receiver=config.agent_id,
        message_type="task",
        payload={"action": "sales.create_order", "params": {"customer_id": 1, "items": []}},
    )
    resp_sales = await agent.handle_message(msg_sales)
    assert resp_sales.message_type == "response"
    assert resp_sales.payload["status"] == "success"
    assert resp_sales.payload["action"] == "sales.create_order"

    # 2. Route to AI Builder Agent
    msg_builder = AgentMessage(
        sender="npub1builderuser",
        receiver=config.agent_id,
        message_type="task",
        payload={"action": "builder.generate_model", "params": {"description": "Product Catalog"}},
    )
    resp_builder = await agent.handle_message(msg_builder)
    assert resp_builder.message_type == "response"
    assert resp_builder.payload["status"] == "success"

    # 3. Route to FE Agent
    msg_fe = AgentMessage(
        sender="npub1feuser",
        receiver=config.agent_id,
        message_type="task",
        payload={
            "action": "fattura_elettronica.generate_xml",
            "params": {
                "invoice_number": "INV-2026-002",
                "invoice_date": "2026-09-02",
                "supplier": {"name": "Vendor"},
                "customer": {"name": "Buyer"},
                "lines": [],
            },
        },
    )
    resp_fe = await agent.handle_message(msg_fe)
    assert resp_fe.message_type == "response"
    assert resp_fe.payload["result"]["status"] == "generated"
