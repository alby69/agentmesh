"""Workflow and Webhook automation module agent."""

from __future__ import annotations

from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class WorkflowAgent(ERPModuleAgent):
    """Specialized agent for Workflow rules and Webhook subscriptions."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="workflow",
            capabilities=[
                "erp.workflow.create_automation",
                "erp.webhook.register",
                "workflow.create_automation",
                "webhook.register",
            ],
            bridge=bridge,
        )

    async def create_automation(
        self, rule_name: str, trigger_event: str, action: str, tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"rule_name": rule_name, "trigger_event": trigger_event, "action": action}
        return await self.execute_module_action("workflow.create_automation", params, tenant_id=tenant_id, api_key=api_key)
