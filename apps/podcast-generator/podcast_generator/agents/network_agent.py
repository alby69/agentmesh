from typing import Optional
from agentmesh.relay.agent import NostrAgent
from podcast_generator.config import Settings

class NetworkAgent(NostrAgent):
    """Podcast-specific NetworkAgent extending AgentMesh Relay."""

    async def publish_podcast(self, title: str, ipfs_cid: str, metadata: dict):
        """Publishes a podcast episode as a Nostr event using Mesh Relay."""
        return await self.publish_file_metadata(title, ipfs_cid, metadata)
