import pytest
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.fe_agent import FEAgent
from erpseed_agent.bridge.vault_bridge import ERPSeedVaultBridge


@pytest.mark.asyncio
async def test_fattura_elettronica_generation_and_ipfs_vault():
    config = ERPSeedConfig(ipfs_provider="mock")
    vault_bridge = ERPSeedVaultBridge(config=config)
    await vault_bridge.start()

    fe_agent = FEAgent(config=config, vault_bridge=vault_bridge)

    res = await fe_agent.generate_fattura_xml(
        invoice_number="INV-2026-999",
        invoice_date="2026-09-02",
        supplier={"name": "Azienda Italiana SRL", "vat_id": "IT09876543210"},
        customer={"name": "Cliente Estero SPA", "sdi_code": "0000000"},
        lines=[
            {"description": "Sviluppo Software AgentMesh", "quantity": 10, "unit_price": 150.0},
            {"description": "Manutenzione Server", "quantity": 1, "unit_price": 300.0},
        ],
    )

    assert res["status"] == "generated"
    assert res["invoice_number"] == "INV-2026-999"
    assert res["ipfs_cid"].startswith("Qm")
    assert "https://ipfs.io/ipfs/" in res["ipfs_url"]
    assert "FPR12" in res["xml_content"]
    assert "Sviluppo Software AgentMesh" in res["xml_content"]

    await vault_bridge.stop()
