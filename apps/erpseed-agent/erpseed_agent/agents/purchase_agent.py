"""Purchase module agent for vendor orders, goods receipts, and supplier invoices."""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class PurchaseAgent(ERPModuleAgent):
    """Specialized agent for Procurement operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="purchases",
            capabilities=[
                "erp.purchases.create_order",
                "erp.purchases.list_orders",
                "purchases.create_order",
                "purchases.list_orders",
            ],
            bridge=bridge,
        )

    async def create_purchase_order(
        self, supplier_id: int, items: List[Dict[str, Any]], tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"supplier_id": supplier_id, "items": items}
        return await self.execute_module_action("purchases.create_order", params, tenant_id=tenant_id, api_key=api_key)
