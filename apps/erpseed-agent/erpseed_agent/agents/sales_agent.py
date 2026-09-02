"""Sales module agent for quotes, sales orders, and customer invoices."""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class SalesAgent(ERPModuleAgent):
    """Specialized agent for Sales operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="sales",
            capabilities=[
                "erp.sales.create_order",
                "erp.sales.list_orders",
                "erp.sales.create_invoice",
                "sales.create_order",
                "sales.list_orders",
                "sales.create_invoice",
            ],
            bridge=bridge,
        )

    async def create_sales_order(
        self, customer_id: int, items: List[Dict[str, Any]], tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"customer_id": customer_id, "items": items}
        return await self.execute_module_action("sales.create_order", params, tenant_id=tenant_id, api_key=api_key)
