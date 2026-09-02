"""Base class for ERPSEED specialized domain sub-agents."""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from agentmesh.core import BaseAgent
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.bridge.executor import ERPSeedBridge

logger = logging.getLogger(__name__)


class ERPModuleAgent(BaseAgent):
    """Base class for specialized ERP module agents."""

    def __init__(
        self,
        config: ERPSeedConfig,
        module_name: str,
        capabilities: List[str],
        bridge: Optional[ERPSeedBridge] = None,
    ):
        super().__init__(config)
        self.module_name = module_name
        self.capabilities = capabilities
        self.bridge = bridge or ERPSeedBridge(
            base_url=config.erpseed_base_url,
            service_jwt=config.erpseed_service_jwt,
        )

    async def start(self) -> None:
        """Starts module agent."""
        self.logger.info(f"Started ERPModuleAgent: {self.module_name}")

    async def stop(self) -> None:
        """Stops module agent."""
        self.logger.info(f"Stopped ERPModuleAgent: {self.module_name}")

    async def can_handle(self, action: str) -> bool:
        """Checks if this agent can handle the given action name."""
        return any(
            action == cap or action.startswith(f"{self.module_name}.")
            for cap in self.capabilities
        )

    async def execute_module_action(
        self, action: str, params: Dict[str, Any], tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        """Executes action via ERPSeedBridge."""
        self.logger.info(f"[{self.module_name.upper()}] Executing action '{action}' for tenant {tenant_id}")
        return await self.bridge.execute(
            action=action,
            params=params,
            tenant_id=tenant_id,
            api_key=api_key,
        )
