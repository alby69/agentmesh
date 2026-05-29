import asyncio
from typing import Optional, List
from agentmesh.core import BaseAgent, MeshConfig

try:
    from nostr_sdk import (
        Client,
        Keys,
        EventBuilder,
        Tag,
        Event,
        Filter,
    )
except ImportError:
    Client = None
    Tag = None

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

    async def publish_file_metadata(self, title: str, ipfs_cid: str, metadata: dict = None):
        """Implements NIP-94 style file metadata publishing (Kind 1063)."""
        content = f"File: {title}\nCID: {ipfs_cid}"
        # NIP-94 Tags: x (sha256), url, m (mime), alt, etc.
        tags = [
            Tag.parse(["url", f"https://ipfs.io/ipfs/{ipfs_cid}"]),
            Tag.parse(["x", ipfs_cid]), # Usually sha256, but CID is often used here
            Tag.parse(["alt", content]),
            Tag.parse(["title", title]),
        ]
        if metadata:
            if "mime" in metadata:
                tags.append(Tag.parse(["m", metadata["mime"]]))
            if "size" in metadata:
                tags.append(Tag.parse(["size", str(metadata["size"])]))

        return await self.publish_event(1063, "", tags)
