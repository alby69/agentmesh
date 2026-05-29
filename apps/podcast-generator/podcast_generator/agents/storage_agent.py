from agentmesh.vault.agent import VaultAgent
from podcast_generator.config import Settings

class StorageAgent(VaultAgent):
    """Podcast-specific StorageAgent extending AgentMesh Vault."""

    def __init__(self, config: Settings):
        super().__init__(config, provider=config.ipfs_provider, gateway_url=config.ipfs_gateway_url)
