from typing import Optional
from agentmesh.core import MeshOrchestrator
from podcast_generator.agents.content_agent import ContentAgent
from podcast_generator.agents.network_agent import NetworkAgent
from podcast_generator.agents.storage_agent import StorageAgent
from agentmesh.core.knowledge import KnowledgeAgent
from agentmesh.core.economy import WalletAgent
from podcast_generator.config import Settings

_agents_instance = None

class AgentsManager(MeshOrchestrator):
    def __init__(self, config: Settings):
        super().__init__(config)
        self.content = ContentAgent(config)
        self.network = NetworkAgent(config)
        self.storage = StorageAgent(config)
        self.knowledge = KnowledgeAgent(config)
        self.wallet = WalletAgent(config)

        self.register_agent("content", self.content)
        self.register_agent("network", self.network)
        self.register_agent("storage", self.storage)
        self.register_agent("knowledge", self.knowledge)
        self.register_agent("wallet", self.wallet)

def get_agents(config: Optional[Settings] = None) -> AgentsManager:
    global _agents_instance
    if _agents_instance is None:
        if config is None:
            from podcast_generator.config import Settings
            config = Settings()
        _agents_instance = AgentsManager(config)
    return _agents_instance
