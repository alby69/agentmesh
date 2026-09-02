"""Tenant resolver bridge for mapping Nostr identities (npub/pubkey) to ERPSEED tenant IDs."""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from erpseed_agent.web.db import get_tenant_mapping, set_tenant_mapping


logger = logging.getLogger(__name__)


class TenantResolver:
    """Resolves AgentMesh sender identities to ERPSEED tenant contexts."""

    def __init__(self, default_tenant_id: int = 1, strict_mode: bool = False):
        self.default_tenant_id = default_tenant_id
        self.strict_mode = strict_mode

    async def resolve(self, sender_pubkey: str) -> Dict[str, Any]:
        """
        Resolves sender pubkey/npub to tenant context dict containing:
        - tenant_id (int)
        - api_key (str)
        """
        mapping = get_tenant_mapping(sender_pubkey)
        if mapping:
            return {
                "tenant_id": mapping["tenant_id"],
                "api_key": mapping.get("api_key", ""),
            }

        if self.strict_mode:
            raise ValueError(f"No tenant mapping registered for sender: {sender_pubkey}")

        logger.info(
            f"Sender {sender_pubkey} has no registered tenant mapping. Falling back to default tenant ID {self.default_tenant_id}"
        )
        return {
            "tenant_id": self.default_tenant_id,
            "api_key": "",
        }

    def register_tenant(self, sender_pubkey: str, tenant_id: int, api_key: str = "") -> None:
        """Registers or updates a sender pubkey to tenant ID mapping."""
        set_tenant_mapping(sender_pubkey, tenant_id, api_key)
        logger.info(f"Registered tenant mapping: {sender_pubkey} -> tenant_id={tenant_id}")
