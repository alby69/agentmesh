import logging
import asyncio
from typing import Optional, List
from agentmesh.core import MeshConfig
from agentmesh.relay.agent import NostrAgent

try:
    from nostr_sdk import Tag
except ImportError:
    Tag = None

logger = logging.getLogger("econnet.relay.publisher")

class EconNetNostrPublisher:
    def __init__(self, private_key: Optional[str] = None, relay_urls: Optional[List[str]] = None):
        self.private_key = private_key
        self.relay_urls = relay_urls or ["wss://relay.damus.io", "wss://nos.lol"]
        self.agent: Optional[NostrAgent] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        config = MeshConfig(
            agent_id="econnet-publisher",
            agent_name="EconNet Nostr Publisher",
            agent_description="Publishes EconNet simulation events to Nostr"
        )
        try:
            self.agent = NostrAgent(config, secret_key=private_key, relays=self.relay_urls)
        except Exception as e:
            logger.error(f"Failed to initialize NostrAgent: {e}. Gracefully falling back.")
            self.agent = None

    async def connect(self):
        if self.agent:
            try:
                await self.agent.start()
                logger.info("EconNetNostrPublisher successfully connected to relays.")
            except Exception as e:
                logger.error(f"Failed to connect NostrAgent: {e}")

    async def disconnect(self):
        if self.agent:
            try:
                await self.agent.stop()
            except Exception as e:
                logger.error(f"Failed to stop NostrAgent: {e}")

    async def publish_price_change(self, tick: int, price: float, old_price: float, producer_id: int):
        if not self.agent:
            return
        content = f"PriceChange at tick {tick}: Producer {producer_id} changed price from {old_price:.2f} to {price:.2f}"
        tags = []
        if Tag:
            tags = [
                Tag.parse(["e", "econnet-price"]),
                Tag.parse(["tick", str(tick)]),
                Tag.parse(["price", str(price)]),
                Tag.parse(["producer_id", str(producer_id)])
            ]
        try:
            # Publish as standard text note (Kind 1)
            await self.agent.publish_event(1, content, tags)
            logger.info(f"Published price change event to Nostr for tick {tick}.")
        except Exception as e:
            logger.warning(f"Failed to publish price change to Nostr: {e}")

    async def publish_transaction(self, tick: int, buyer_id: int, seller_id: int, price: float, quantity: int, amount: float, credit: bool):
        if not self.agent:
            return
        pay_type = "credit" if credit else "cash"
        content = f"Transaction at tick {tick}: Buyer {buyer_id} bought {quantity} units from {seller_id} for {amount:.2f} via {pay_type}"
        tags = []
        if Tag:
            tags = [
                Tag.parse(["e", "econnet-tx"]),
                Tag.parse(["tick", str(tick)]),
                Tag.parse(["buyer_id", str(buyer_id)]),
                Tag.parse(["seller_id", str(seller_id)]),
                Tag.parse(["price", str(price)]),
                Tag.parse(["quantity", str(quantity)]),
                Tag.parse(["use_credit", "1" if credit else "0"])
            ]
        try:
            await self.agent.publish_event(1, content, tags)
        except Exception as e:
            logger.warning(f"Failed to publish transaction to Nostr: {e}")

    async def publish_market_crash(self, tick: int, return_rate: float, price: float):
        if not self.agent:
            return
        content = f"MarketCrash at tick {tick}: Market dropped by {return_rate * 100:.1f}%, current price: {price:.2f}"
        tags = []
        if Tag:
            tags = [
                Tag.parse(["e", "econnet-crash"]),
                Tag.parse(["tick", str(tick)]),
                Tag.parse(["return_rate", str(return_rate)]),
                Tag.parse(["price", str(price)])
            ]
        try:
            await self.agent.publish_event(1, content, tags)
        except Exception as e:
            logger.warning(f"Failed to publish market crash to Nostr: {e}")
