"""Specialized ERPSeed Agent implementation for AgentMesh."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from agentmesh.core import BaseAgent, AgentMessage
from agentmesh.llm.base import BaseLLMProvider

from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.bridge.executor import ERPSeedBridge
from erpseed_agent.bridge.tenant_resolver import TenantResolver
from erpseed_agent.bridge.capability_sync import CapabilitySync
from erpseed_agent.web.db import log_agent_action

logger = logging.getLogger(__name__)


class ERPSeedAgent(BaseAgent):
    """
    Specialized agent for Enterprise Resource Planning operations, fiscal compliance,
    and dynamic model generation in AgentMesh.
    """

    def __init__(
        self,
        config: ERPSeedConfig,
        llm_provider: Optional[BaseLLMProvider] = None,
        bridge: Optional[ERPSeedBridge] = None,
        tenant_resolver: Optional[TenantResolver] = None,
        capability_sync: Optional[CapabilitySync] = None,
    ):
        super().__init__(config)
        self.erp_config = config
        self.llm = llm_provider
        self.capabilities = [
            "erp.sales",
            "erp.purchases",
            "erp.inventory",
            "erp.accounting",
            "erp.hr",
            "erp.builder",
            "erp.workflow",
            "erp.reporting",
        ]

        self.bridge = bridge or ERPSeedBridge(
            base_url=config.erpseed_base_url,
            service_jwt=config.erpseed_service_jwt,
        )
        self.tenant_resolver = tenant_resolver or TenantResolver()
        self.capability_sync = capability_sync or CapabilitySync(
            base_url=config.erpseed_base_url,
            service_jwt=config.erpseed_service_jwt,
            agent_id=config.agent_id,
        )

    async def start(self) -> None:
        """Starts the agent, verifies backend connectivity, and syncs capabilities."""
        self.logger.info(f"Starting {self.config.agent_name} ({self.config.agent_id})...")
        healthy = await self.bridge.health_check()
        if healthy:
            self.logger.info("ERPSeed backend health check passed.")
        else:
            self.logger.warning("ERPSeed backend health check failed. Agent will run in offline mode.")

        # Sync capabilities from ERPSEED backend
        synced_caps = await self.capability_sync.fetch_and_translate()
        self.logger.info(f"Advertised {len(synced_caps)} capabilities from ERPSEED manifest.")

    async def stop(self) -> None:
        """Stops the agent and closes network bridges."""
        self.logger.info(f"Stopping {self.config.agent_name}...")
        await self.bridge.close()
        await self.capability_sync.close()
        self.logger.info("ERPSeedAgent stopped.")

    async def sync_capabilities(self) -> List[Any]:
        """Manually trigger capability synchronization."""
        return await self.capability_sync.fetch_and_translate()

    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """
        Handles incoming A2A messages from other mesh agents.
        Processes 'task' messages by routing actions to ERPSEED backend with tenant isolation.
        """
        self.logger.info(f"Received message type '{message.message_type}' from {message.sender}")

        if message.message_type != "task":
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="info",
                payload={
                    "status": "ignored",
                    "reason": f"Unsupported message_type: {message.message_type}. Expected 'task'.",
                },
            )

        payload = message.payload or {}
        action = payload.get("action", "")
        params = payload.get("params", {})

        if not action:
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="error",
                payload={"status": "error", "reason": "Missing 'action' in task payload."},
            )

        # 1. Resolve tenant context from sender identity
        try:
            tenant_ctx = await self.tenant_resolver.resolve(message.sender)
            tenant_id = tenant_ctx["tenant_id"]
            api_key = tenant_ctx.get("api_key", "")
        except Exception as e:
            self.logger.error(f"Tenant resolution failed for {message.sender}: {e}")
            log_agent_action(message.id, message.sender, action, "tenant_error", str(e))
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="error",
                payload={"status": "error", "action": action, "reason": f"Tenant resolution failed: {e}"},
            )

        # 2. Execute via ERPSEED Bridge
        try:
            result = await self.bridge.execute(
                action=action,
                params=params,
                tenant_id=tenant_id,
                api_key=api_key,
            )
            log_agent_action(message.id, message.sender, action, "success", f"Tenant {tenant_id}")
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="response",
                payload={
                    "status": "success",
                    "action": action,
                    "tenant_id": tenant_id,
                    "result": result,
                },
            )
        except Exception as e:
            self.logger.error(f"Execution failed for action '{action}': {e}")
            log_agent_action(message.id, message.sender, action, "execution_error", str(e))
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="error",
                payload={
                    "status": "error",
                    "action": action,
                    "tenant_id": tenant_id,
                    "reason": str(e),
                },
            )
