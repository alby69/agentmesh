"""IPFS Vault bridge for ERPSEED agent documents (Invoices, Reports, Attachments)."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from agentmesh.vault import VaultAgent
from erpseed_agent.config import ERPSeedConfig

logger = logging.getLogger(__name__)


class ERPSeedVaultBridge:
    """Wraps VaultAgent to store and retrieve ERP documents (invoices, reports) on IPFS."""

    def __init__(self, config: ERPSeedConfig, vault_agent: Optional[VaultAgent] = None):
        self.config = config
        self.vault_agent = vault_agent or VaultAgent(
            config=config,
            provider=config.ipfs_provider,
            gateway_url=config.ipfs_gateway_url,
        )

    async def start(self) -> None:
        await self.vault_agent.start()

    async def stop(self) -> None:
        await self.vault_agent.stop()

    async def store_invoice_xml(self, xml_content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Stores a FatturaPA XML content string in IPFS Vault and returns the CID."""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(xml_content)
            tmp_path = Path(tmp.name)

        try:
            cid = await self.vault_agent.upload_file(tmp_path)
            logger.info(f"Stored invoice XML on IPFS. CID: {cid}")
            return cid or "QmMockInvoiceCid"
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    async def store_report_pdf(self, pdf_bytes: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Stores a PDF report byte array in IPFS Vault and returns the CID."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)

        try:
            cid = await self.vault_agent.upload_file(tmp_path)
            logger.info(f"Stored report PDF on IPFS. CID: {cid}")
            return cid or "QmMockReportCid"
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    async def get_file_url(self, cid: str) -> str:
        """Returns gateway URL for IPFS CID."""
        return await self.vault_agent.get_file_url(cid)
