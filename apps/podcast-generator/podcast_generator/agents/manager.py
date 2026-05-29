from typing import Optional
from agentmesh.core import MeshOrchestrator
from podcast_generator.agents.content_agent import ContentAgent
from podcast_generator.agents.network_agent import NetworkAgent
from podcast_generator.agents.storage_agent import StorageAgent
from podcast_generator.agents.social_agent import SocialAgent
from podcast_generator.config import Settings

_agents_instance = None

class AgentsManager(MeshOrchestrator):
    def __init__(self, config: Settings):
        super().__init__(config)
        self.content = ContentAgent(config)
        self.network = NetworkAgent(config)
        self.storage = StorageAgent(config)
        # SocialAgent in podcast-generator/agents/social_agent.py only takes config in its __init__
        # but the original logic might have passed network_agent.
        # Checking social_agent.py, it only takes (self, config: Settings).
        self.social = SocialAgent(config)

        self.register_agent("content", self.content)
        self.register_agent("network", self.network)
        self.register_agent("storage", self.storage)
        self.register_agent("social", self.social)

def get_agents(config: Optional[Settings] = None) -> AgentsManager:
    global _agents_instance
    if _agents_instance is None:
        if config is None:
            from podcast_generator.config import Settings
            config = Settings()
        _agents_instance = AgentsManager(config)
    return _agents_instance
