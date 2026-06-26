from typing import Optional
from agentmesh.relay.agent import NostrAgent
from podcast_generator.config import Settings

class NetworkAgent(NostrAgent):
    """Podcast-specific NetworkAgent extending AgentMesh Relay."""

    async def publish_podcast(self, title: str, ipfs_cid: str, metadata: dict):
        """Publishes a podcast episode as a Nostr event using Mesh Relay."""
        return await self.publish_file_metadata(title, ipfs_cid, metadata)

    async def discover_podcasts(self):
        """Discovers podcast episodes on the network."""
        # For PoC, we search for Kind 1063 (File Metadata) events
        # In a real mesh, we would use the KnowledgeAgent to score results
        events = await self.search_capabilities("podcast") # This is a placeholder for actual podcast search logic
        results = []
        for e in events:
             results.append({
                 "title": e.name,
                 "url": e.metadata.get("url", f"https://ipfs.io/ipfs/{e.agent_id}"),
                 "pubkey": e.public_key
             })
        return results
