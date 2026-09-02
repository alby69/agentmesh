"""CRM module agent for leads, opportunities, pipelines, and customer contracts."""

from __future__ import annotations

from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class CRMAgent(ERPModuleAgent):
    """Specialized agent for CRM operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="crm",
            capabilities=[
                "erp.crm.create_lead",
                "erp.crm.list_opportunities",
                "crm.create_lead",
                "crm.list_opportunities",
            ],
            bridge=bridge,
        )

    async def create_lead(
        self, company_name: str, contact_email: str, tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"company_name": company_name, "contact_email": contact_email}
        return await self.execute_module_action("crm.create_lead", params, tenant_id=tenant_id, api_key=api_key)
