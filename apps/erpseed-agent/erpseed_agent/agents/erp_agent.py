"""Specialized ERPSeed Agent implementation for AgentMesh with Nostr A2A and sub-agent orchestration."""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Dict
from agentmesh.relay import NostrAgent
from agentmesh.core import AgentMessage
from agentmesh.llm.base import BaseLLMProvider

from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.bridge.executor import ERPSeedBridge
from erpseed_agent.bridge.tenant_resolver import TenantResolver
from erpseed_agent.bridge.capability_sync import CapabilitySync
from erpseed_agent.bridge.vault_bridge import ERPSeedVaultBridge
from erpseed_agent.bridge.nostr_relay import NostrRelayBridge

from erpseed_agent.agents.sales_agent import SalesAgent
from erpseed_agent.agents.purchase_agent import PurchaseAgent
from erpseed_agent.agents.inventory_agent import InventoryAgent
from erpseed_agent.agents.accounting_agent import AccountingAgent
from erpseed_agent.agents.hr_agent import HRAgent
from erpseed_agent.agents.manufacturing_agent import ManufacturingAgent
from erpseed_agent.agents.crm_agent import CRMAgent
from erpseed_agent.agents.fe_agent import FEAgent
from erpseed_agent.agents.workflow_agent import WorkflowAgent
from erpseed_agent.agents.ai_builder_agent import AIBuilderAgent
from erpseed_agent.web.db import log_agent_action

logger = logging.getLogger(__name__)


class ERPSeedAgent(NostrAgent):
    """
    Main ERPSeed Agent for AgentMesh.
    Inherits from NostrAgent to communicate over Nostr relays (Kind 29001/30311),
    and orchestrates specialized modular sub-agents (Sales, Purchases, Inventory, FE, AI Builder, etc.).
    """

    def __init__(
        self,
        config: ERPSeedConfig,
        llm_provider: Optional[BaseLLMProvider] = None,
        bridge: Optional[ERPSeedBridge] = None,
        tenant_resolver: Optional[TenantResolver] = None,
        capability_sync: Optional[CapabilitySync] = None,
        vault_bridge: Optional[ERPSeedVaultBridge] = None,
    ):
        secret_key = config.nostr_private_key if config.nostr_private_key else None
        relays = config.nostr_relays or [config.nostr_relay_url]
        super().__init__(config=config, secret_key=secret_key, relays=relays)

        self.erp_config = config
        self.llm = llm_provider

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
        self.vault_bridge = vault_bridge or ERPSeedVaultBridge(config=config)
        self.nostr_relay_bridge = NostrRelayBridge(agent=self, config=config)

        # Initialize modular sub-agents
        self.sales_agent = SalesAgent(config=config, bridge=self.bridge)
        self.purchase_agent = PurchaseAgent(config=config, bridge=self.bridge)
        self.inventory_agent = InventoryAgent(config=config, bridge=self.bridge)
        self.accounting_agent = AccountingAgent(config=config, bridge=self.bridge)
        self.hr_agent = HRAgent(config=config, bridge=self.bridge)
        self.manufacturing_agent = ManufacturingAgent(config=config, bridge=self.bridge)
        self.crm_agent = CRMAgent(config=config, bridge=self.bridge)
        self.fe_agent = FEAgent(config=config, vault_bridge=self.vault_bridge, bridge=self.bridge)
        self.workflow_agent = WorkflowAgent(config=config, bridge=self.bridge)
        self.ai_builder_agent = AIBuilderAgent(config=config, bridge=self.bridge)

        self.sub_agents = [
            self.sales_agent,
            self.purchase_agent,
            self.inventory_agent,
            self.accounting_agent,
            self.hr_agent,
            self.manufacturing_agent,
            self.crm_agent,
            self.fe_agent,
            self.workflow_agent,
            self.ai_builder_agent,
        ]

        self.capabilities = [
            "erp.sales",
            "erp.purchases",
            "erp.inventory",
            "erp.accounting",
            "erp.hr",
            "erp.manufacturing",
            "erp.crm",
            "erp.fattura_elettronica",
            "erp.builder",
            "erp.workflow",
        ]

    async def start(self) -> None:
        """Starts NostrAgent, checks ERPSEED backend health, and syncs capabilities."""
        self.logger.info(f"Starting {self.config.agent_name} ({self.config.agent_id})...")
        await super().start()
        await self.vault_bridge.start()

        healthy = await self.bridge.health_check()
        if healthy:
            self.logger.info("ERPSeed backend health check passed.")
        else:
            self.logger.warning("ERPSeed backend health check failed. Agent running in standalone/offline mode.")

        synced_caps = await self.sync_capabilities()
        self.logger.info(f"Advertised {len(synced_caps)} capabilities from ERPSEED manifest.")

    async def stop(self) -> None:
        """Stops NostrAgent, closes network bridges, and releases resources."""
        self.logger.info(f"Stopping {self.config.agent_name}...")
        await self.vault_bridge.stop()
        await self.bridge.close()
        await self.capability_sync.close()
        await super().stop()
        self.logger.info("ERPSeedAgent stopped.")

    async def sync_capabilities(self) -> List[Any]:
        """Fetch and synchronize capabilities from backend and broadcast to Nostr."""
        synced = await self.capability_sync.fetch_and_translate()
        cap_names = self.capabilities + [c.name for c in synced]
        await self.nostr_relay_bridge.broadcast_capability(cap_names)
        return synced

    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """
        Handles incoming A2A messages from other mesh agents over Nostr or direct call.
        Routes action requests to specialized sub-agents or bridge with tenant isolation.
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

        # 2. Dispatch action to appropriate sub-agent or execution bridge
        try:
            result = await self._dispatch_action(action=action, params=params, tenant_id=tenant_id, api_key=api_key)
            log_agent_action(message.id, message.sender, action, "success", f"Tenant {tenant_id}")

            response_msg = AgentMessage(
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

            # Publish response back via Nostr if receiver is specified
            if message.sender:
                await self.nostr_relay_bridge.send_a2a_response(
                    receiver_pubkey=message.sender, action=action, result=result
                )

            return response_msg

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

    async def _dispatch_action(
        self, action: str, params: Dict[str, Any], tenant_id: int, api_key: str
    ) -> Dict[str, Any]:
        """Dispatches an action to specialized sub-agents or bridge."""
        if action.startswith("builder.") or action.startswith("erp.builder."):
            if "generate_model" in action:
                return await self.ai_builder_agent.generate_model(
                    description=params.get("description", "custom entity"),
                    model_name=params.get("model_name"),
                )
            elif "generate_view" in action:
                return await self.ai_builder_agent.generate_view(
                    model_name=params.get("model_name", "entity"),
                    view_type=params.get("view_type", "list"),
                )
            elif "generate_workflow" in action:
                return await self.ai_builder_agent.generate_workflow(
                    workflow_name=params.get("workflow_name", "wf_rule"),
                    description=params.get("description", ""),
                )

        if action.startswith("fattura_elettronica.generate_xml") or action.startswith("erp.fattura_elettronica.generate_xml"):
            return await self.fe_agent.generate_fattura_xml(
                invoice_number=params.get("invoice_number", "INV-001"),
                invoice_date=params.get("invoice_date", "2026-09-02"),
                supplier=params.get("supplier", {"name": "ERPSEED Corp", "vat_id": "12345678901"}),
                customer=params.get("customer", {"name": "Client SRL", "sdi_code": "0000000"}),
                lines=params.get("lines", [{"description": "Service fee", "quantity": 1, "unit_price": 100.0}]),
                tenant_id=tenant_id,
            )

        # Check all modular sub-agents
        for sub_agent in self.sub_agents:
            if await sub_agent.can_handle(action):
                return await sub_agent.execute_module_action(
                    action=action, params=params, tenant_id=tenant_id, api_key=api_key
                )

        # Generic CQRS or dynamic API fallback bridge
        return await self.bridge.execute(action=action, params=params, tenant_id=tenant_id, api_key=api_key)
