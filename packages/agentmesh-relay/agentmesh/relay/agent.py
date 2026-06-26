import asyncio
import json
from typing import Optional, List, Dict, Any, Callable
from agentmesh.core import BaseAgent, MeshConfig
from agentmesh.core.models import AgentCapability, AgentMessage

try:
    from nostr_sdk import (
        Client,
        Keys,
        EventBuilder,
        Tag,
        Event,
        Filter,
        Kind,
        UnsignedEvent,
        Nip44,
    )
except ImportError:
    Client = None
    Tag = None
    Kind = None

# Custom Kind for Agent Registry (inspired by NIP-31 but focused on AgentMesh)
KIND_AGENT_REGISTRY = 30311
# Kind for encrypted Agent Messages
KIND_AGENT_MESSAGE = 29001

class NostrAgent(BaseAgent):
    """Handles P2P identity and communication using the Nostr protocol."""

    def __init__(self, config: MeshConfig, secret_key: Optional[str] = None, relays: List[str] = None):
        super().__init__(config)
        if Client is None:
            self.logger.error("nostr-sdk not installed. NostrAgent will be dysfunctional.")
            self.client = None
            return

        if secret_key:
            self.keys = Keys.parse(secret_key)
        else:
            self.keys = Keys.generate()

        self.client = Client(self.keys)
        self.relays = relays or ["wss://relay.damus.io", "wss://nos.lol", "wss://relay.snort.social"]
        self._message_handlers: Dict[str, List[Callable]] = {}

    async def start(self):
        if not self.client:
            return

        for relay in self.relays:
            await self.client.add_relay(relay)

        await self.client.connect()
        self.logger.info(f"Connected to Nostr as {self.keys.public_key().to_bech32()}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()

    async def publish_event(self, kind: int, content: str, tags: List[Tag] = None):
        if not self.client:
            return

        event = EventBuilder(kind, content, tags or []).to_event(self.keys)
        event_id = await self.client.send_event(event)
        return event_id

    async def publish_capability(self, capability: AgentCapability):
        """Publishes agent capabilities to the registry."""
        content = capability.model_dump_json()
        tags = [
            Tag.parse(["d", capability.agent_id]),
            Tag.parse(["label", "agentmesh-capability"])
        ]
        for cap in capability.capabilities:
            tags.append(Tag.parse(["t", cap]))

        return await self.publish_event(KIND_AGENT_REGISTRY, content, tags)

    async def send_message(self, message: AgentMessage):
        """Sends a standardized AgentMessage (encrypted if receiver is set)."""
        content = message.model_dump_json()
        tags = []

        if message.receiver:
            # Encrypted message (NIP-44)
            # In a real scenario, we'd need to fetch the receiver's public key object
            # and use nip44 encrypt. For this PoC, we'll store as plaintext in kind 29001
            # with a receiver tag.
            tags.append(Tag.parse(["p", message.receiver]))

        return await self.publish_event(KIND_AGENT_MESSAGE, content, tags)

    async def search_capabilities(self, skill: str) -> List[AgentCapability]:
        """Searches for agents with specific capabilities."""
        if not self.client:
            return []

        filter = Filter().kind(KIND_AGENT_REGISTRY).hashtag(skill)
        events = await self.client.get_events_of([filter], asyncio.timedelta(seconds=5))

        results = []
        for event in events:
            try:
                cap = AgentCapability.model_validate_json(event.content())
                results.append(cap)
            except Exception as e:
                self.logger.warning(f"Failed to parse capability event: {e}")

        return results

    async def publish_file_metadata(self, title: str, ipfs_cid: str, metadata: dict = None):
        """Implements NIP-94 style file metadata publishing (Kind 1063)."""
        content = f"File: {title}\nCID: {ipfs_cid}"
        tags = [
            Tag.parse(["url", f"https://ipfs.io/ipfs/{ipfs_cid}"]),
            Tag.parse(["x", ipfs_cid]),
            Tag.parse(["alt", content]),
            Tag.parse(["title", title]),
        ]
        if metadata:
            if "mime" in metadata:
                tags.append(Tag.parse(["m", metadata["mime"]]))
            if "size" in metadata:
                tags.append(Tag.parse(["size", str(metadata["size"])]))

        return await self.publish_event(1063, "", tags)
