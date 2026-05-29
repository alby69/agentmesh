from agentmesh.core import BaseAgent, MeshConfig

class ProjectAgent(BaseAgent):
    """Manages the lifecycle of a project in MoTeDico."""
    async def start(self):
        self.logger.info("ProjectAgent started.")
    async def stop(self):
        pass

class AdvisorAgent(BaseAgent):
    """Generates advice using LLM for projects."""
    async def start(self):
        self.logger.info("AdvisorAgent started.")
    async def stop(self):
        pass
