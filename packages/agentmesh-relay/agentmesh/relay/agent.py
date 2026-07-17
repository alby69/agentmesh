import asyncio
import time
from typing import Optional, List, Dict, Any
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
        HandleNotification,
        NostrSigner,
        RelayUrl,
    )
except ImportError:
    Client = None
    Keys = None
    EventBuilder = None
    Tag = None
    Event = object
    Filter = None
    Kind = None
    UnsignedEvent = None
    HandleNotification = object
    NostrSigner = None
    RelayUrl = None

# Custom Kind for Agent Registry (inspired by NIP-31 but focused on AgentMesh)
KIND_AGENT_REGISTRY = 30311
# Kind for encrypted Agent Messages
KIND_AGENT_MESSAGE = 29001

class MeshNotificationHandler(HandleNotification):
    def __init__(self, agent: 'NostrAgent'):
        self.agent = agent

    async def handle(self, relay_url: str, event: Event):
        await self.agent._process_incoming_event(event)

    async def handle_msg(self, relay_url: str, msg: Any):
        pass

class NostrAgent(BaseAgent):
    """Handles P2P identity and communication using the Nostr protocol."""

    def __init__(self, config: MeshConfig, secret_key: Optional[str] = None, relays: List[str] = None):
        super().__init__(config)

        # Simple Rate Limiting: pubkey -> [timestamps]
        self._rate_limits: Dict[str, List[float]] = {}
        self._rate_limit_window = 60.0  # seconds
        self._rate_limit_max_msgs = 10  # max messages per window
        self._listening_task: Optional[asyncio.Task] = None

        if Client is None:
            self.logger.error("nostr-sdk not installed. NostrAgent will be dysfunctional.")
            self.client = None
            return

        if secret_key:
            self.keys = Keys.parse(secret_key)
        else:
            self.keys = Keys.generate()

        signer = NostrSigner.keys(self.keys)
        self.client = Client(signer)
        self.relays = relays or ["wss://relay.damus.io", "wss://nos.lol", "wss://relay.snort.social"]

    async def start(self):
        if not self.client:
            return

        for relay in self.relays:
            if RelayUrl is not None and isinstance(relay, str):
                relay = RelayUrl.parse(relay)
            await self.client.add_relay(relay)

        await self.client.connect()
        self.logger.info(f"Connected to Nostr as {self.keys.public_key().to_bech32()}")

        # Start listening for messages addressed to this agent
        await self._start_listening()

    async def stop(self):
        if self._listening_task:
            self._listening_task.cancel()
        if self.client:
            await self.client.disconnect()

    async def _start_listening(self):
        """Sets up a subscription for incoming AgentMessages."""
        pubkey = self.keys.public_key().to_hex()
        # Filter for Agent Messages (Kind 29001) addressed to this agent (p-tag)
        # Also listen for broadcast messages (no p-tag, handled by client logic)
        msg_filter = Filter().kind(Kind(KIND_AGENT_MESSAGE)).pubkey(pubkey)
        await self.client.subscribe([msg_filter])

        self.logger.info(f"Subscribed to AgentMessages for {pubkey}")

        # In a real scenario, we'd use the HandleNotification callback
        # For this implementation, we'll poll for now or use the SDK's built-in event loop if available
        # Note: nostr-sdk-python handles notifications via a separate thread or async task
        self.client.handle_notifications(MeshNotificationHandler(self))

    def _is_rate_limited(self, pubkey: str) -> bool:
        """Checks if a pubkey is exceeding the rate limit."""
        now = time.time()
        if pubkey not in self._rate_limits:
            self._rate_limits[pubkey] = []

        # Clean up old timestamps
        self._rate_limits[pubkey] = [t for t in self._rate_limits[pubkey] if now - t < self._rate_limit_window]

        if len(self._rate_limits[pubkey]) >= self._rate_limit_max_msgs:
            return True

        self._rate_limits[pubkey].append(now)
        return False

    async def _process_incoming_event(self, event: Event):
        """Processes a received Nostr event and converts it to an AgentMessage."""
        if event.kind() == Kind(KIND_AGENT_MESSAGE):
            # Check if event has author (handle mocks)
            try:
                author = event.author()
                pubkey = author.to_hex() if author else "unknown"
            except Exception:
                pubkey = "unknown"

            if self._is_rate_limited(pubkey):
                self.logger.warning(f"Rate limit exceeded for sender {pubkey}. Ignoring message.")
                return

            try:
                msg = AgentMessage.model_validate_json(event.content())
                self.logger.info(f"Received AgentMessage: {msg.id} from {msg.sender}")
                await self.handle_message(msg)
            except Exception as e:
                self.logger.warning(f"Failed to parse incoming AgentMessage: {e}")

    async def publish_event(self, kind: int, content: str, tags: List[Tag] = None):
        if not self.client:
            return

        event = EventBuilder(Kind(kind), content, tags or []).to_event(self.keys)
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
            tags.append(Tag.parse(["p", message.receiver]))

        return await self.publish_event(KIND_AGENT_MESSAGE, content, tags)

    async def search_capabilities(self, skill: str) -> List[AgentCapability]:
        """Searches for agents with specific capabilities."""
        if not self.client:
            return []

        filter = Filter().kind(Kind(KIND_AGENT_REGISTRY)).hashtag(skill)
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
