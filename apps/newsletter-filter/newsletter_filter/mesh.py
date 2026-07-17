import logging
import time
from typing import Optional, List, Dict, Any

from agentmesh.core import MeshConfig
from agentmesh.core.models import AgentCapability, AgentMessage
from newsletter_filter.web.db import get_articles

logger = logging.getLogger("newsletter_filter.mesh")

try:
    from agentmesh.relay.agent import NostrAgent, KIND_AGENT_MESSAGE
except ImportError:
    NostrAgent = None
    KIND_AGENT_MESSAGE = 29001

FILTER_AGENT_ID = "newsletter-filter-agent"


class FilterMeshAgent(NostrAgent if NostrAgent else object):
    """Nostr-enabled FilterAgent for P2P mesh communication."""

    def __init__(self, config: MeshConfig, secret_key: Optional[str] = None, relays: List[str] = None):
        if NostrAgent is None:
            logger.warning("agentmesh-relay not installed. Nostr features disabled.")
            self.logger = logger
            return
        super().__init__(config, secret_key=secret_key, relays=relays)

    async def register_capabilities(self):
        """Publish filter capabilities to the Nostr registry."""
        if NostrAgent is None:
            return
        cap = AgentCapability(
            agent_id=FILTER_AGENT_ID,
            capabilities=["newsletter-filter", "content-analysis", "semantic-scoring"],
            description="Cognitive newsletter filtering and content extraction agent",
        )
        await self.publish_capability(cap)
        logger.info("FilterAgent capabilities published to Nostr registry.")

    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Handle incoming A2A requests from other agents."""
        if message.message_type == "query":
            criteria = message.payload.get("criteria", "")
            limit = message.payload.get("limit", 10)
            articles = get_articles(relevant_only=True, search_query=criteria, limit=limit)
            results = [
                {
                    "title": a["title"],
                    "url": a["url"],
                    "score": a["score"],
                    "summary": a["summary"],
                    "key_points": a["key_points"],
                }
                for a in articles
            ]
            return AgentMessage(
                sender=FILTER_AGENT_ID,
                receiver=message.sender,
                message_type="response",
                payload={"status": "success", "results": results, "count": len(results)},
            )

        return AgentMessage(
            sender=FILTER_AGENT_ID,
            receiver=message.sender,
            message_type="response",
            payload={"status": "error", "detail": f"Unknown message_type: {message.message_type}"},
        )

    async def publish_articles_to_mesh(self, relevant_only: bool = True, limit: int = 5):
        """Broadcast recent relevant articles as Nostr events."""
        if NostrAgent is None:
            return
        articles = get_articles(relevant_only=relevant_only, limit=limit)
        for article in articles:
            msg = AgentMessage(
                sender=FILTER_AGENT_ID,
                message_type="broadcast",
                payload={
                    "type": "article",
                    "title": article["title"],
                    "url": article["url"],
                    "score": article["score"],
                    "summary": article["summary"],
                },
            )
            await self.send_message(msg)
        logger.info(f"Published {len(articles)} articles to Nostr mesh.")


# A2A Economy: micropayment tracking
_micropayment_ledger: Dict[str, Dict[str, Any]] = {}


def verify_cashu_token(token: str) -> bool:
    """Verify a Cashu Lightning token (stub implementation).

    In production this would validate the Cashu token signature and amount
    against a mint. For now it accepts any non-empty token.
    """
    if not token:
        return False
    return True


def record_micropayment(sender: str, amount_sats: int, token: str, query: str) -> Dict[str, Any]:
    """Record a micropayment and return receipt."""
    record = {
        "sender": sender,
        "amount_sats": amount_sats,
        "token": token,
        "query": query,
        "timestamp": time.time(),
    }
    _micropayment_ledger[sender] = record
    logger.info(f"Micropayment recorded: {amount_sats} sats from {sender} for query '{query}'")
    return record


def get_micropayment_history(sender: Optional[str] = None) -> List[Dict[str, Any]]:
    if sender:
        rec = _micropayment_ledger.get(sender)
        return [rec] if rec else []
    return list(_micropayment_ledger.values())
