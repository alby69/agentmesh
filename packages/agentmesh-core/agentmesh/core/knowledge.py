import asyncio
import logging
from typing import List, Dict, Any, Optional
from agentmesh.core import BaseAgent, MeshConfig
from agentmesh.core.models import AgentMessage, AgentReputation, KnowledgeFact

class KnowledgeAgent(BaseAgent):
    """
    Evolution of the Social Agent. Manages distributed memory,
    shared knowledge graphs, and reputation via Nostr events.
    """

    def __init__(self, config: MeshConfig):
        super().__init__(config)
        self.capabilities = ["knowledge-management", "reputation-scoring", "wot-verification"]
        self.knowledge_graph: List[KnowledgeFact] = []
        self.reputation_db: Dict[str, AgentReputation] = {}

    async def start(self):
        self.logger.info("KnowledgeAgent active. Building shared memory...")

    async def stop(self):
        pass

    async def ingest_fact(self, fact: KnowledgeFact):
        """Adds a new fact to the local knowledge graph."""
        self.knowledge_graph.append(fact)
        self.logger.info(f"Ingested fact: {fact.subject} {fact.predicate} {fact.object}")

    async def get_reputation(self, agent_id: str) -> AgentReputation:
        """Retrieves or calculates the reputation of an agent."""
        if agent_id not in self.reputation_db:
            # Initialize with default
            self.reputation_db[agent_id] = AgentReputation(agent_id=agent_id)
        return self.reputation_db[agent_id]

    async def update_reputation(self, agent_id: str, feedback_score: float):
        """Updates an agent's reputation based on new feedback (0.0 to 1.0)."""
        rep = await self.get_reputation(agent_id)
        # Simple moving average for PoC
        n = rep.reviews_count
        rep.score = (rep.score * n + feedback_score) / (n + 1)
        rep.reviews_count += 1
        rep.last_updated = asyncio.get_event_loop().time()
        self.logger.info(f"Updated reputation for {agent_id}: {rep.score:.2f} ({rep.reviews_count} reviews)")

    async def query_knowledge(self, query: str) -> List[KnowledgeFact]:
        """Simple keyword search in the knowledge graph."""
        results = [f for f in self.knowledge_graph if query.lower() in f.subject.lower() or query.lower() in f.object.lower()]
        return results

    async def handle_message(self, message: AgentMessage):
        if message.message_type == "info" and message.payload.get("action") == "get_reputation":
            target_id = message.payload.get("agent_id")
            if target_id:
                rep = await self.get_reputation(target_id)
                # In a real implementation, we would send a response message
                self.logger.info(f"Reputation request for {target_id}: {rep.score}")
