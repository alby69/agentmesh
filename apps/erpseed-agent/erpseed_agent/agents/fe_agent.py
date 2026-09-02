"""Fattura Elettronica PA 1.2 XML generation & IPFS Vault agent."""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.vault_bridge import ERPSeedVaultBridge
from erpseed_agent.bridge.executor import ERPSeedBridge

logger = logging.getLogger(__name__)


class FEAgent(ERPModuleAgent):
    """Specialized agent for Italian FatturaPA 1.2 electronic invoicing and IPFS archiving."""

    def __init__(
        self,
        config: ERPSeedConfig,
        vault_bridge: Optional[ERPSeedVaultBridge] = None,
        bridge: Optional[ERPSeedBridge] = None,
    ):
        super().__init__(
            config=config,
            module_name="fattura_elettronica",
            capabilities=[
                "erp.fattura_elettronica.generate_xml",
                "erp.fattura_elettronica.send_sdi",
                "fattura_elettronica.generate_xml",
                "fattura_elettronica.send_sdi",
            ],
            bridge=bridge,
        )
        self.vault_bridge = vault_bridge or ERPSeedVaultBridge(config=config)

    async def generate_fattura_xml(
        self,
        invoice_number: str,
        invoice_date: str,
        supplier: Dict[str, Any],
        customer: Dict[str, Any],
        lines: list,
        tenant_id: int = 1,
    ) -> Dict[str, Any]:
        """Generates FatturaPA 1.2 XML string and stores it on IPFS via Vault Bridge."""
        xml_lines = []
        for line in lines:
            desc = line.get("description", "Articolo")
            qty = line.get("quantity", 1)
            price = line.get("unit_price", 0.0)
            tot = qty * price
            xml_lines.append(
                f"<DettaglioLinee><NumeroLinea>{len(xml_lines)+1}</NumeroLinea><Descrizione>{desc}</Descrizione>"
                f"<Quantita>{qty}</Quantita><PrezzoUnitario>{price}</PrezzoUnitario><PrezzoTotale>{tot}</PrezzoTotale></DettaglioLinee>"
            )

        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2">
  <FatturaElettronicaHeader>
    <DatiTrasmissione>
      <IdTrasmittente><IdPaese>IT</IdPaese><IdCodice>{supplier.get('vat_id', '00000000000')}</IdCodice></IdTrasmittente>
      <ProgressivoInvio>{invoice_number}</ProgressivoInvio>
      <FormatoTrasmissione>FPR12</FormatoTrasmissione>
      <CodiceDestinatario>{customer.get('sdi_code', '0000000')}</CodiceDestinatario>
    </DatiTrasmissione>
    <CedentePrestatore>
      <DatiAnagrafici><Anagrafica><Denominazione>{supplier.get('name', 'Cedente')}</Denominazione></Anagrafica></DatiAnagrafici>
    </CedentePrestatore>
    <CessionarioCommittente>
      <DatiAnagrafici><Anagrafica><Denominazione>{customer.get('name', 'Committente')}</Denominazione></Anagrafica></DatiAnagrafici>
    </CessionarioCommittente>
  </FatturaElettronicaHeader>
  <FatturaElettronicaBody>
    <DatiGenerali>
      <DatiGeneraliDocumento>
        <TipologiaDocumento>TD01</TipologiaDocumento>
        <Divisa>EUR</Divisa>
        <Data>{invoice_date}</Data>
        <Numero>{invoice_number}</Numero>
      </DatiGeneraliDocumento>
    </DatiGenerali>
    <DatiBeniServizi>
      {''.join(xml_lines)}
    </DatiBeniServizi>
  </FatturaElettronicaBody>
</p:FatturaElettronica>"""

        # Store in IPFS
        cid = await self.vault_bridge.store_invoice_xml(xml_content, metadata={"invoice_number": invoice_number})
        url = await self.vault_bridge.get_file_url(cid)

        return {
            "status": "generated",
            "invoice_number": invoice_number,
            "ipfs_cid": cid,
            "ipfs_url": url,
            "xml_content": xml_content,
        }
