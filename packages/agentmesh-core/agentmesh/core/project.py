import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel
from agentmesh.core import BaseAgent, MeshConfig
from agentmesh.core.models import AgentMessage

class ProjectBlueprint(BaseModel):
    project_id: str
    name: str
    members: List[str] # List of pubkeys
    workflow_steps: List[Dict[str, Any]]

class ProjectAgent(BaseAgent):
    """
    Represents an autonomous project. It maintains long-term state,
    coordinates members, and manages project memory on IPFS.
    """

    def __init__(self, config: MeshConfig, blueprint: ProjectBlueprint):
        super().__init__(config)
        self.blueprint = blueprint
        self.capabilities = ["project-management", "governance", "state-persistence"]
        self.state = {"status": "active", "version": 1}

    async def start(self):
        self.logger.info(f"ProjectAgent for '{self.blueprint.name}' started.")

    async def stop(self):
        # In a real implementation, we would save state to IPFS here
        pass

    async def sync_state(self, vault_agent):
        """Saves project state to the distributed storage layer."""
        self.logger.info("Syncing project state to IPFS...")
        data = {
            "blueprint": self.blueprint.model_dump(),
            "state": self.state
        }
        # In a real implementation:
        # cid = await vault_agent.upload_data(json.dumps(data))
        # self.logger.info(f"Project state synced to CID: {cid}")
        # return cid
        return "mock-cid-for-state"

    async def add_member(self, pubkey: str):
        """Adds a new member to the project."""
        if pubkey not in self.blueprint.members:
            self.blueprint.members.append(pubkey)
            self.logger.info(f"Added member {pubkey} to project {self.blueprint.name}")

    async def handle_message(self, message: AgentMessage):
        if message.sender not in self.blueprint.members:
            self.logger.warning(f"Received unauthorized message from {message.sender}")
            return

        if message.message_type == "info" and message.payload.get("action") == "get_status":
            self.logger.info(f"Reporting status to {message.sender}")
            # Send response message logic here
