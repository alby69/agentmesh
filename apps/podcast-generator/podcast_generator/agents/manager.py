from typing import Optional, Dict, Callable, Any
from agentmesh.core import MeshOrchestrator
from podcast_generator.agents.content_agent import ContentAgent
from podcast_generator.agents.network_agent import NetworkAgent
from podcast_generator.agents.storage_agent import StorageAgent
from agentmesh.core.knowledge import KnowledgeAgent
from agentmesh.core.economy import WalletAgent
from podcast_generator.config import Settings

_agents_instance = None

class AgentsManager(MeshOrchestrator):
    def __init__(self, config: Settings, agent_factories: Optional[Dict[str, Callable]] = None):
        super().__init__(config)

        if agent_factories:
            for name, factory in agent_factories.items():
                agent = factory(config)
                self.register_agent(name, agent)
                setattr(self, name, agent)
        else:
            # Default agents
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
    """Backward compatible singleton-like getter, though now it can be instantiated multiple times if needed."""
    global _agents_instance
    if _agents_instance is None:
        if config is None:
            config = Settings()
        _agents_instance = AgentsManager(config)
    return _agents_instance

def create_agents_manager(config: Settings) -> AgentsManager:
    """Factory function to create a new AgentsManager instance."""
    return AgentsManager(config)
