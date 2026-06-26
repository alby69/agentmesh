import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from pydantic_settings import BaseSettings
from agentmesh.core.models import AgentCapability, AgentMessage

class MeshConfig(BaseSettings):
    """Base configuration for AgentMesh."""
    agent_id: str = "base-agent"
    agent_name: str = "Base Agent"
    agent_description: str = "An AgentMesh specialized worker"
    agent_version: str = "0.1.0"

class BaseAgent(ABC):
    """Base class for all specialized agents in AgentMesh."""

    def __init__(self, config: MeshConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.capabilities: List[str] = []

    @abstractmethod
    async def start(self):
        """Initialize and start the agent's background tasks."""
        pass

    @abstractmethod
    async def stop(self):
        """Gracefully stop the agent."""
        pass

    async def emit_event(self, event_type: str, data: Any):
        """Emit an event that other agents or the system might be interested in."""
        self.logger.info(f"Event Emitted: {event_type} - {data}")

    # Agentic Economy (v3.5)
    async def request_payment(self, amount_sats: int, description: str) -> str:
        """Generates a payment request (Lightning/Cashu)."""
        self.logger.info(f"Requesting payment of {amount_sats} sats for: {description}")
        # Integration point for agentstr-sdk / LNURL-pay
        return f"lnbc{amount_sats}mockinvoice..."

    async def verify_payment(self, payment_hash: str) -> bool:
        """Verifies if a payment has been settled."""
        self.logger.info(f"Verifying payment: {payment_hash}")
        # Check against Lightning Node or Cashu Mint
        return True

    async def handle_message(self, message: AgentMessage):
        """Callback to handle incoming AgentMessages."""
        self.logger.info(f"Received message of type {message.message_type} from {message.sender}")

class MeshOrchestrator:
    def __init__(self, config: MeshConfig):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self._started = False

    def register_agent(self, name: str, agent: BaseAgent):
        self.agents[name] = agent

    async def start(self):
        if self._started:
            return
        for name, agent in self.agents.items():
            await agent.start()
        self._started = True

    async def stop(self):
        if not self._started:
            return
        for name, agent in self.agents.items():
            await agent.stop()
        self._started = False

    def get_agent_capability(self, agent_name: str, public_key: str) -> AgentCapability:
        """Constructs a capability object for a registered agent."""
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found in orchestrator.")

        return AgentCapability(
            agent_id=self.config.agent_id,
            name=self.config.agent_name,
            description=self.config.agent_description,
            version=self.config.agent_version,
            public_key=public_key,
            capabilities=agent.capabilities
        )
