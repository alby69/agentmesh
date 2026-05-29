import asyncio
import hashlib
from typing import Optional, Dict, Any
from podcast_generator.agents.base import BaseAgent
from podcast_generator.config import Settings

try:
    from nostr_sdk import (
        Client,
        Keys,
        EventBuilder,
        Tag,
        Metadata,
        Event,
        Nip19Event,
        Filter,
        HandleNotification,
        RelayOptions,
        ClientBuilder,
        Kind,
        NostrSigner,
        RelayUrl
    )
except ImportError:
    # Fallback for environment where nostr-sdk is not yet installed
    Client = None
    Kind = None
    NostrSigner = None
    RelayUrl = None

class NetworkAgent(BaseAgent):
    """Handles P2P identity and communication using the Nostr protocol."""

    def __init__(self, config: Settings, secret_key: Optional[str] = None):
        super().__init__(config)
        if Client is None:
            self.logger.error("nostr-sdk not installed. NetworkAgent will be dysfunctional.")
            self.client = None
            return

        sk = secret_key or self.config.nostr_secret_key
        if sk:
            try:
                self.keys = Keys.parse(sk)
            except Exception as e:
                self.logger.error(f"Failed to parse secret key: {e}. Generating new keys.")
                self.keys = Keys.generate()
        else:
            self.keys = Keys.generate()

        signer = NostrSigner.keys(self.keys)
        self.client = Client(signer)
        self.relays = self.config.nostr_relays

    async def start(self):
        if not self.client:
            return

        for relay in self.relays:
            try:
                # In newer versions of nostr-sdk, we might need RelayUrl object
                url = RelayUrl.parse(relay) if RelayUrl else relay
                await self.client.add_relay(url)
            except Exception as e:
                self.logger.error(f"Failed to add relay {relay}: {e}")

        await self.client.connect()
        self.logger.info(f"Connected to Nostr as {self.keys.public_key().to_bech32()}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()

    async def publish_podcast(self, title: str, ipfs_cid: str, file_path: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Publishes a podcast episode as a Nostr event using NIP-94 (File Metadata)."""
        if not self.client:
            return

        metadata = metadata or {}
        content = f"New Podcast Episode: {title}"
        file_url = f"ipfs://{ipfs_cid}"
        gateway_url = f"{self.config.ipfs_gateway_url}{ipfs_cid}"

        # Calculate file hash if path provided
        file_hash = ""
        if file_path:
            from pathlib import Path
            p = Path(file_path)
            if p.exists():
                file_hash = hashlib.sha256(p.read_bytes()).hexdigest()

        # NIP-94 File Metadata (Kind 1063)
        # NIP-94 tags: url, m (mime), x (sha256), alt, summary, etc.
        tags = [
            Tag.parse(["url", gateway_url]),
            Tag.parse(["m", "audio/mpeg"]),
            Tag.parse(["alt", f"Podcast episode: {title}"]),
            Tag.parse(["title", title]),
            Tag.parse(["t", "podcastgen"])
        ]

        if file_hash:
            tags.append(Tag.parse(["x", file_hash]))

        if ipfs_cid:
            tags.append(Tag.parse(["r", file_url]))

        # We publish both a Kind 1 (Note) for human readability and a Kind 1063 (Metadata)

        # 1. NIP-94 Event (Kind 1063)
        try:
            # Kind(1063) might not be explicitly named in older nostr-sdk versions
            kind_1063 = Kind(1063) if Kind else 1063
            file_event = EventBuilder(kind_1063, "", tags).to_event(self.keys)
            file_event_id = await self.client.send_event(file_event)
            self.logger.info(f"Published NIP-94 File Metadata event: {file_event_id.to_bech32()}")
        except Exception as e:
            self.logger.error(f"Error publishing NIP-94 event: {e}")
            file_event_id = None

        # 2. Kind 1 Note with a reference to the file event
        note_content = f"{content}\n\nListen here: {gateway_url}"
        note_tags = [Tag.parse(["t", "podcastgen"])]
        if file_event_id:
             note_tags.append(Tag.parse(["e", file_event_id.to_hex()]))

        note_event = EventBuilder(1, note_content, note_tags).to_event(self.keys)
        note_event_id = await self.client.send_event(note_event)
        self.logger.info(f"Published Kind 1 note: {note_event_id.to_bech32()}")

        return note_event_id
