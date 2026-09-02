"""Inventory module agent for warehouse movements, stock levels, and lot tracking."""

from __future__ import annotations

from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class InventoryAgent(ERPModuleAgent):
    """Specialized agent for Warehouse and Inventory operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="inventory",
            capabilities=[
                "erp.inventory.move_stock",
                "erp.inventory.check_stock",
                "erp.inventory.track_lot",
                "inventory.move_stock",
                "inventory.check_stock",
                "inventory.track_lot",
            ],
            bridge=bridge,
        )

    async def move_stock(
        self, product_id: int, quantity: float, source_loc: str, target_loc: str, tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {
            "product_id": product_id,
            "quantity": quantity,
            "source_location": source_loc,
            "target_location": target_loc,
        }
        return await self.execute_module_action("inventory.move_stock", params, tenant_id=tenant_id, api_key=api_key)
