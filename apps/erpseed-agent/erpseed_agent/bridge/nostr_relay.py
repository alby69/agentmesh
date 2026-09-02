"""Nostr Relay Bridge for dispatching A2A messages, domain events, and file metadata."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, List

from agentmesh.core import AgentMessage, AgentCapability
from agentmesh.relay import NostrAgent
from erpseed_agent.config import ERPSeedConfig

logger = logging.getLogger(__name__)


class NostrRelayBridge:
    """Helper bridge for managing Nostr communication on top of NostrAgent."""

    def __init__(self, agent: NostrAgent, config: ERPSeedConfig):
        self.agent = agent
        self.config = config

    async def broadcast_capability(self, capabilities_list: List[str]) -> Any:
        """Publishes capability manifest to Nostr Agent Registry (Kind 30311)."""
        pubkey = self.agent.keys.public_key().to_hex() if hasattr(self.agent, "keys") and self.agent.keys else "npub_erpseed"
        cap = AgentCapability(
            agent_id=self.config.agent_id,
            name=self.config.agent_name,
            description=self.config.agent_description,
            version=self.config.agent_version,
            public_key=pubkey,
            capabilities=capabilities_list,
        )
        logger.info(f"Broadcasting capabilities to Nostr registry for {self.config.agent_id}: {capabilities_list}")
        return await self.agent.publish_capability(cap)

    async def send_a2a_response(self, receiver_pubkey: str, action: str, result: Dict[str, Any]) -> Optional[AgentMessage]:
        """Sends an A2A response message back to the requesting agent over Nostr (Kind 29001)."""
        msg = AgentMessage(
            sender=self.config.agent_id,
            receiver=receiver_pubkey,
            message_type="response",
            payload={
                "action": action,
                "status": "success",
                "result": result,
            },
        )
        await self.agent.send_message(msg)
        return msg

    async def publish_invoice_metadata(self, title: str, ipfs_cid: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Publishes NIP-94 style file metadata event (Kind 1063) on Nostr."""
        return await self.agent.publish_file_metadata(title=title, ipfs_cid=ipfs_cid, metadata=metadata or {})
