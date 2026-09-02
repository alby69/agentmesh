import pytest
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.llm.tools import get_builder_tools, execute_tool
from erpseed_agent.llm.builder_service import ERPSeedBuilderService


def test_builder_tools_schema():
    tools = get_builder_tools()
    assert len(tools) >= 3
    tool_names = [t["name"] for t in tools]
    assert "generate_model_schema" in tool_names
    assert "generate_view_layout" in tool_names
    assert "generate_workflow_rule" in tool_names


def test_execute_tool():
    res = execute_tool("generate_model_schema", {"model_name": "customer", "fields": []})
    assert res["model_name"] == "customer"
    assert res["table_name"] == "tbl_customer"

    res_view = execute_tool("generate_view_layout", {"model_name": "customer", "view_type": "kanban"})
    assert res_view["view_type"] == "kanban"


@pytest.mark.asyncio
async def test_builder_service():
    config = ERPSeedConfig(llm_provider="ollama")
    service = ERPSeedBuilderService(config=config)

    model_res = await service.generate_model("Invoices for Clients", model_name="client_invoice")
    assert "model_name" in model_res or "status" in model_res

    view_res = await service.generate_view("client_invoice", "form")
    assert "view_type" in view_res or "status" in view_res

    wf_res = await service.generate_workflow("invoice_approval", "Approve invoices over 1000 EUR")
    assert "workflow_name" in wf_res or "status" in wf_res
