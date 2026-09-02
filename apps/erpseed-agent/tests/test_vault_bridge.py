import pytest
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.bridge.vault_bridge import ERPSeedVaultBridge


@pytest.mark.asyncio
async def test_vault_bridge_store_invoice_and_report():
    config = ERPSeedConfig(ipfs_provider="mock")
    bridge = ERPSeedVaultBridge(config=config)
    await bridge.start()

    xml_data = "<FatturaElettronica><Header>Test</Header></FatturaElettronica>"
    xml_cid = await bridge.store_invoice_xml(xml_data)
    assert xml_cid.startswith("Qm")

    pdf_data = b"%PDF-1.4 test invoice report"
    pdf_cid = await bridge.store_report_pdf(pdf_data)
    assert pdf_cid.startswith("Qm")

    url = await bridge.get_file_url(xml_cid)
    assert url == f"https://ipfs.io/ipfs/{xml_cid}"

    await bridge.stop()
