from typing import List, Optional
from agentmesh.core import BaseAgent, MeshConfig
from agentmesh.core.models import AgentMessage
from podcast_generator.config import Settings
from podcast_generator.models import Newsletter, Episode

class TaskAgent(BaseAgent):
    """
    The orchestrator that receives high-level requests and delegates
    them to specialized agents (Content, Storage, Network).
    """

    def __init__(self, config: Settings):
        super().__init__(config)
        self.capabilities = ["orchestration", "podcast-task-management"]
        self._content_agent = None
        self._storage_agent = None
        self._network_agent = None

    async def start(self):
        self.logger.info("TaskAgent started and ready to orchestrate.")

    async def stop(self):
        pass

    def set_agents(self, content_agent, storage_agent, network_agent):
        """Manually wire agents for the local mesh (PoC)."""
        self._content_agent = content_agent
        self._storage_agent = storage_agent
        self._network_agent = network_agent

    async def run_podcast_workflow(self, newsletter_url: str):
        """
        Orchestrates the full podcast generation workflow.
        In a full v3 implementation, this would use discovery to find agents.
        """
        self.logger.info(f"Starting workflow for {newsletter_url}")

        if not self._content_agent or not self._storage_agent or not self._network_agent:
            self.logger.error("Agents not properly wired in TaskAgent.")
            return

        # 1. Content Generation
        self.logger.info("Step 1: Fetching and Generating Episode Content...")
        newsletter = await self._content_agent.fetch_latest() # Assuming it uses config if no URL
        episode = await self._content_agent.generate_episode_from_newsletter(newsletter)

        # 2. Storage
        self.logger.info("Step 2: Uploading to Distributed Storage (IPFS)...")
        cid = await self._storage_agent.upload_file(episode.audio_path)
        self.logger.info(f"Content pinned with CID: {cid}")

        # 3. Network Announcement
        self.logger.info("Step 3: Announcing on P2P Mesh (Nostr)...")
        metadata = {
            "duration": episode.duration_minutes,
            "date": episode.date_str,
            "url": episode.url
        }
        event_id = await self._network_agent.publish_podcast(episode.title, cid, metadata)
        self.logger.info(f"Podcast announced on Nostr. Event ID: {event_id}")

        return {
            "title": episode.title,
            "cid": cid,
            "nostr_event": event_id
        }

    async def handle_message(self, message: AgentMessage):
        """Handle incoming tasks via the message bus."""
        if message.message_type == "task" and message.payload.get("action") == "generate_podcast":
            url = message.payload.get("url")
            await self.run_podcast_workflow(url)
