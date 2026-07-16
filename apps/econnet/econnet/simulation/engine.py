import random
import logging
from typing import Any, Dict, List, Optional

from econnet.agents.consumer import ConsumerAgent
from econnet.agents.producer import ProducerAgent
from econnet.network.social_graph import SocialGraph
from econnet.simulation.market import Market
from econnet.simulation.events import EventBus, Event

logger = logging.getLogger("econnet.simulation.engine")


class SimulationEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None, seed: int = 42):
        self.config = config or {}
        self.seed = seed
        self.rng = random.Random(seed)
        self.tick = 0
        self._ticks_executed = 0
        self.consumers: List[ConsumerAgent] = []
        self.producers: List[ProducerAgent] = []
        self.social_graph = SocialGraph(seed=seed)
        self.market = Market()
        self.event_bus = EventBus()
        self.tick_log: List[Dict[str, Any]] = []
        self._running = False

    def setup(
        self,
        num_consumers: int = 100,
        num_producers: int = 10,
        consumer_budget: float = 100.0,
        producer_budget: float = 500.0,
        initial_price: float = 10.0,
        network_type: str = "small-world",
    ) -> None:
        for i in range(num_producers):
            cost = self.rng.uniform(3.0, 7.0)
            price = initial_price * self.rng.uniform(0.8, 1.2)
            stock = self.rng.randint(30, 80)
            p = ProducerAgent(
                agent_id=i,
                budget=producer_budget,
                cost_per_unit=cost,
                initial_stock=stock,
                price=price,
                production_rate=self.rng.randint(5, 15),
            )
            self.producers.append(p)

        for i in range(num_consumers):
            c = ConsumerAgent(
                agent_id=num_producers + i,
                budget=consumer_budget * self.rng.uniform(0.5, 1.5),
                risk_aversion=self.rng.uniform(0.1, 0.9),
                social_susceptibility=self.rng.uniform(0.1, 0.9),
                anchoring=self.rng.uniform(0.1, 0.7),
            )
            self.consumers.append(c)

        all_ids = [p.id for p in self.producers] + [c.id for c in self.consumers]

        if network_type == "random":
            self.social_graph.build_random(all_ids, edge_probability=0.05)
        elif network_type == "small-world":
            self.social_graph.build_small_world(all_ids, k=6, p=0.1)
        elif network_type == "scale-free":
            self.social_graph.build_scale_free(all_ids, m=3)
        else:
            self.social_graph.build_random(all_ids, edge_probability=0.05)

        for c in self.consumers:
            c.neighbors = self.social_graph.get_neighbors(c.id)

        logger.info(
            "Setup: %d consumers, %d producers, %d network edges",
            num_consumers, num_producers, self.social_graph.edge_count(),
        )

    def run(self, max_ticks: int = 500, verbose: bool = False) -> List[Dict[str, Any]]:
        self._running = True
        self.tick_log = []

        for t in range(max_ticks):
            if not self._running:
                break
            tick_data = self._run_tick(t)
            self.tick_log.append(tick_data)
            self._ticks_executed = t + 1
            if verbose and t % 50 == 0:
                logger.info(
                    "Tick %d: price=%.2f, volume=%d, consumers=%d, producers=%d",
                    t, tick_data["price"], tick_data["volume"],
                    len(self.consumers), len(self.producers),
                )

        self._running = False
        return self.tick_log

    def _run_tick(self, tick: int) -> Dict[str, Any]:
        self.market.reset_tick()
        self.tick = tick

        self.event_bus.emit(Event("tick_start", tick))

        producer_actions = []
        for producer in self.producers:
            avg_price = sum(p.price for p in self.producers) / max(len(self.producers), 1)
            market_state = {
                "total_demand": sum(
                    1 for c in self.consumers
                    if c.needs_level > 0.5 and producer.price <= c.budget * 0.4
                ),
                "competitor_avg_price": avg_price,
            }
            actions = producer.step(tick, market_state)
            producer_actions.extend(actions)

            if producer.stock > 0:
                self.market.submit_sell(
                    agent_id=producer.id,
                    price=producer.price,
                    quantity=min(producer.stock, 5),
                    tick=tick,
                )

        consumer_emotions = {c.id: c.emotional_state[0] for c in self.consumers}
        neighbor_satisfactions = self.social_graph.get_all_neighbor_satisfactions(consumer_emotions)

        consumer_actions = []
        for consumer in self.consumers:
            market_state = {
                "current_price": self.market.get_current_price(),
                "avg_neighbor_satisfaction": neighbor_satisfactions.get(consumer.id, 0.5),
            }
            actions = consumer.step(tick, market_state)
            consumer_actions.extend(actions)

            for action in actions:
                if action["type"] == "buy" and action["quantity"] > 0:
                    self.market.submit_buy(
                        agent_id=consumer.id,
                        price=action["price"],
                        quantity=action["quantity"],
                        tick=tick,
                    )

        transactions = self.market.match_orders(tick)

        for tx in transactions:
            buyer = next((c for c in self.consumers if c.id == tx.buyer_id), None)
            seller = next((p for p in self.producers if p.id == tx.seller_id), None)
            if buyer and seller:
                buyer.spend(tx.amount)
                seller.sell(tx.quantity, tx.price)
                buyer.on_purchase(tx.price, tx.quantity)

            self.event_bus.emit(Event(
                "transaction", tick,
                {"buyer": tx.buyer_id, "seller": tx.seller_id, "price": tx.price, "quantity": tx.quantity},
            ))

        self.social_graph.evolve(creation_rate=0.02, removal_rate=0.005)

        tick_data = self.market.finalize_tick(tick)
        tick_data["consumers"] = len(self.consumers)
        tick_data["producers"] = len(self.producers)
        tick_data["transactions_detail"] = [
            {"buyer": tx.buyer_id, "seller": tx.seller_id, "price": tx.price, "quantity": tx.quantity}
            for tx in transactions
        ]

        avg_emotion = sum(c.emotional_state[0] for c in self.consumers) / max(len(self.consumers), 1)
        tick_data["avg_consumer_satisfaction"] = round(avg_emotion, 3)

        return tick_data

    def stop(self) -> None:
        self._running = False

    def get_agent_states(self) -> List[Dict[str, Any]]:
        states = [p.to_dict() for p in self.producers]
        states.extend(c.to_dict() for c in self.consumers)
        return states

    def get_summary(self) -> Dict[str, Any]:
        market_stats = self.market.get_statistics()
        return {
            "ticks": self._ticks_executed,
            "consumers": len(self.consumers),
            "producers": len(self.producers),
            "network_edges": self.social_graph.edge_count(),
            "network_density": round(self.social_graph.density(), 4),
            "avg_clustering": round(self.social_graph.avg_clustering(), 4),
            "market": market_stats,
            "events_total": self.event_bus.get_event_count(),
            "transactions_total": self.event_bus.get_event_count("transaction"),
        }
