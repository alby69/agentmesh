"""Manufacturing module agent for Bill of Materials (BOM), production orders, and MRP."""

from __future__ import annotations

from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class ManufacturingAgent(ERPModuleAgent):
    """Specialized agent for Manufacturing, BOM, and MRP operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="manufacturing",
            capabilities=[
                "erp.manufacturing.get_bom",
                "erp.manufacturing.create_odp",
                "erp.manufacturing.run_mrp",
                "manufacturing.get_bom",
                "manufacturing.create_odp",
                "manufacturing.run_mrp",
            ],
            bridge=bridge,
        )

    async def create_odp(
        self, product_id: int, quantity: float, tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"product_id": product_id, "quantity": quantity}
        return await self.execute_module_action("manufacturing.create_odp", params, tenant_id=tenant_id, api_key=api_key)
