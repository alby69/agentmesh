"""Accounting module agent for Prima Nota general ledger entries, VAT, and payments."""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class AccountingAgent(ERPModuleAgent):
    """Specialized agent for Accounting and General Ledger operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="accounting",
            capabilities=[
                "erp.accounting.prima_nota",
                "erp.accounting.liquidazione_iva",
                "accounting.prima_nota",
                "accounting.liquidazione_iva",
            ],
            bridge=bridge,
        )

    async def register_prima_nota(
        self, date: str, entries: List[Dict[str, Any]], tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"date": date, "entries": entries}
        return await self.execute_module_action("accounting.prima_nota", params, tenant_id=tenant_id, api_key=api_key)
