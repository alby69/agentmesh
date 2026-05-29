import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from pydantic_settings import BaseSettings

class MeshConfig(BaseSettings):
    """Base configuration for AgentMesh."""
    pass

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
