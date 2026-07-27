import random
import logging
from typing import Any, Dict, List, Optional

from econnet.agents.consumer import ConsumerAgent
from econnet.agents.producer import ProducerAgent
from econnet.network.social_graph import SocialGraph
from econnet.simulation.market import Market
from econnet.simulation.events import (
    EventBus, Event, PriceChangeEvent, TransactionEvent, AgentDecisionEvent, MarketCrashEvent
)

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

        # Graeberian properties
        self.graeber_active = self.config.get("graeber", False)
        self.social_peace = self.config.get("initial_peace", 1.0)
        self.tribute_rate = self.config.get("tribute_rate", 0.05)

        # Graeberian cumulative statistics
        self.total_mutual_aid_count = 0
        self.total_mutual_aid_volume = 0.0
        self.total_tributes_paid = 0.0
        self.total_charity_paid = 0.0
        self.total_credit_sales_volume = 0.0
        self.total_defaults_count = 0
        self.total_defaulted_losses = 0.0

    def setup(
        self,
        num_consumers: int = 100,
        num_producers: int = 10,
        consumer_budget: float = 100.0,
        producer_budget: float = 500.0,
        initial_price: float = 10.0,
        network_type: str = "small-world",
    ) -> None:
        self.graeber_active = self.config.get("graeber", False)
        self.social_peace = self.config.get("initial_peace", 1.0)
        self.tribute_rate = self.config.get("tribute_rate", 0.05)

        self.consumers.clear()
        self.producers.clear()

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
                use_rl=self.config.get("use_rl", True),
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
                    "Tick %d: price=%.2f, volume=%d, consumers=%d, producers=%d, social_peace=%.2f",
                    t, tick_data["price"], tick_data["volume"],
                    len(self.consumers), len(self.producers), self.social_peace
                )

        self._running = False
        return self.tick_log

    def _calculate_gini(self) -> float:
        budgets = [c.budget for c in self.consumers] + [p.budget for p in self.producers]
        if not budgets:
            return 0.0
        sorted_budgets = sorted(budgets)
        n = len(sorted_budgets)
        total_sum = sum(sorted_budgets)
        if n == 0 or total_sum == 0:
            return 0.0
        cumulative_sum = 0.0
        for i, val in enumerate(sorted_budgets):
            cumulative_sum += (i + 1) * val
        return (2.0 * cumulative_sum) / (n * total_sum) - (n + 1.0) / n

    def _run_tick(self, tick: int) -> Dict[str, Any]:
        self.market.reset_tick()
        self.tick = tick

        self.event_bus.emit(Event("tick_start", tick))

        # Dynamic Social Peace adjustment based on market and debt situation
        if self.graeber_active:
            self._adjust_social_peace(tick)

        # 1. Base Communism step (Mutual aid/gifting between consumers in need)
        if self.graeber_active and self.social_peace > 0.3:
            self._execute_baseline_communism(tick)

        # 2. Hierarchy step (Tributes/Charity based on class precedence)
        if self.graeber_active:
            self._execute_hierarchy_precedents(tick)

        # 3. Normal Market Cycle (Producer pricing and Consumer buying)
        producer_actions = []
        recent_volume = self.market.volume_history[-1] if self.market.volume_history else 0.0
        avg_consumer_emotion = sum(c.emotional_state[0] for c in self.consumers) / max(len(self.consumers), 1)

        for producer in self.producers:
            avg_price = sum(p.price for p in self.producers) / max(len(self.producers), 1)
            market_state = {
                "total_demand": sum(
                    1 for c in self.consumers
                    if c.needs_level > 0.5 and producer.price <= c.budget * 0.4
                ),
                "competitor_avg_price": avg_price,
                "recent_volume": recent_volume,
                "avg_emotion": avg_consumer_emotion,
            }

            old_price = producer.price
            actions = producer.step(tick, market_state)
            producer_actions.extend(actions)

            # Emit PriceChangeEvent and AgentDecisionEvent
            if producer.price != old_price:
                self.event_bus.emit(PriceChangeEvent(tick, producer.price, old_price, producer.id))

            for action in actions:
                self.event_bus.emit(AgentDecisionEvent(
                    tick, producer.id, "producer", action["type"], action
                ))

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
                "graeber": self.graeber_active,
                "social_peace": self.social_peace,
            }
            actions = consumer.step(tick, market_state)
            consumer_actions.extend(actions)

            for action in actions:
                self.event_bus.emit(AgentDecisionEvent(
                    tick, consumer.id, "consumer", action["type"], action
                ))

            for action in actions:
                if action["type"] == "buy" and action["quantity"] > 0:
                    self.market.submit_buy(
                        agent_id=consumer.id,
                        price=action["price"],
                        quantity=action["quantity"],
                        tick=tick,
                        use_credit=action.get("use_credit", False),
                    )

        # Match buy/sell orders in the market
        transactions = self.market.match_orders(tick)

        # Process transaction financial exchanges
        for tx in transactions:
            buyer = next((c for c in self.consumers if c.id == tx.buyer_id), None)
            seller = next((p for p in self.producers if p.id == tx.seller_id), None)
            if buyer and seller:
                if tx.use_credit:
                    # Graeber credit transaction: Seller extends credit, buyer incurs debt
                    debt_amount = seller.sell_on_credit(buyer.id, tx.quantity, tx.price)
                    buyer.incur_debt(seller.id, debt_amount)
                    buyer.on_purchase(tx.price, tx.quantity)
                    self.total_credit_sales_volume += debt_amount
                else:
                    # Standard cash transaction
                    buyer.spend(tx.amount)
                    seller.sell(tx.quantity, tx.price)
                    buyer.on_purchase(tx.price, tx.quantity)

            # Emit TransactionEvent
            self.event_bus.emit(TransactionEvent(
                tick, tx.buyer_id, tx.seller_id, tx.price, tx.quantity, tx.amount, tx.use_credit
            ))

        # 4. Debt Servicing / Repayment / Cash Squeeze
        if self.graeber_active:
            self._handle_debt_repayment_or_default(tick)

        # Social Graph evolution
        self.social_graph.evolve(creation_rate=0.02, removal_rate=0.005)

        tick_data = self.market.finalize_tick(tick)
        tick_data["consumers"] = len(self.consumers)
        tick_data["producers"] = len(self.producers)
        tick_data["transactions_detail"] = [
            {"buyer": tx.buyer_id, "seller": tx.seller_id, "price": tx.price, "quantity": tx.quantity, "credit": tx.use_credit}
            for tx in transactions
        ]

        # Check and emit MarketCrashEvent
        prices = self.market.price_history
        if len(prices) >= 2:
            return_rate = (prices[-1] - prices[-2]) / prices[-2] if prices[-2] != 0 else 0.0
            if return_rate <= -0.05:
                self.event_bus.emit(MarketCrashEvent(tick, return_rate, prices[-1]))

        # Graph herd effect and sentiment metrics
        agent_actions = {}
        for c in self.consumers:
            bought = any(act["agent_id"] == c.id and act["type"] == "buy" for act in consumer_actions)
            agent_actions[c.id] = "buy" if bought else "none"

        herd_effect_val = self.social_graph.calculate_herd_effect(agent_actions)
        sentiment_prop_val = self.social_graph.calculate_sentiment_propagation(consumer_emotions)

        tick_data["avg_consumer_satisfaction"] = round(avg_consumer_emotion, 3)
        tick_data["gini_index"] = round(self._calculate_gini(), 4)
        tick_data["herd_effect"] = round(herd_effect_val, 4)
        tick_data["sentiment_propagation"] = round(sentiment_prop_val, 4)

        # Graeber metric exports for plotting and analysis
        if self.graeber_active:
            tick_data["graeber"] = True
            tick_data["social_peace"] = round(self.social_peace, 3)
            tick_data["total_debt"] = round(sum(sum(c.debts.values()) for c in self.consumers), 2)
            tick_data["mutual_aid_count"] = self.total_mutual_aid_count
            tick_data["mutual_aid_volume"] = round(self.total_mutual_aid_volume, 2)
            tick_data["tributes_paid"] = round(self.total_tributes_paid, 2)
            tick_data["charity_paid"] = round(self.total_charity_paid, 2)
            tick_data["credit_sales_volume"] = round(self.total_credit_sales_volume, 2)
            tick_data["defaults_count"] = self.total_defaults_count
            tick_data["defaulted_losses"] = round(self.total_defaulted_losses, 2)
        else:
            tick_data["graeber"] = False

        return tick_data

    def _adjust_social_peace(self, tick: int) -> None:
        """Co-evolves social peace with market volatility, inequality, and bad debt defaults."""
        volatility = self.market._volatility()
        # High volatility decays social peace
        decay = volatility * 0.2

        # Defaults decay social peace drastically (representing social anger and loss of trust)
        total_recent_defaults = sum(c.defaults_count for c in self.consumers)
        if total_recent_defaults > 0:
            decay += min(0.15, total_recent_defaults * 0.01)

        # Budgets inequality (Gini-like approximation) also decays peace
        high_budgets = sum(1 for c in self.consumers if c.social_class == "high")
        low_budgets = sum(1 for c in self.consumers if c.social_class == "low")
        class_disparities = abs(high_budgets - low_budgets) / max(1, len(self.consumers))
        decay += class_disparities * 0.05

        self.social_peace = max(0.0, min(1.0, self.social_peace - decay + 0.01))

    def _execute_baseline_communism(self, tick: int) -> None:
        """Baseline communism step: neighbor agents help those in need with gifts (no debt)."""
        for consumer in self.consumers:
            if consumer.social_class == "low" and consumer.budget < 30.0:
                # Seek mutual aid from neighbors
                for neighbor_id in consumer.neighbors:
                    neighbor = next((c for c in self.consumers if c.id == neighbor_id), None)
                    if neighbor and neighbor.social_class in ["medium", "high"] and neighbor.budget > 80.0:
                        # Give a gift of 5.0 to 15.0 budget units
                        gift_amount = min(self.rng.uniform(5.0, 15.0), neighbor.budget * 0.15)
                        if neighbor.give_communist_gift(consumer, gift_amount):
                            self.total_mutual_aid_count += 1
                            self.total_mutual_aid_volume += gift_amount
                            break  # limit to one mutual aid gift per tick for simplicity

    def _execute_hierarchy_precedents(self, tick: int) -> None:
        """Hierarchy step: tributes paid to superior class, charity given to inferior class."""
        for consumer in self.consumers:
            if consumer.social_class == "low":
                # Find a wealthy neighbor and pay a small tribute to establish peace/protection
                for neighbor_id in consumer.neighbors:
                    neighbor = next((c for c in self.consumers if c.id == neighbor_id), None)
                    if neighbor and neighbor.social_class == "high" and consumer.budget > 5.0:
                        tribute_amt = consumer.budget * self.tribute_rate
                        if consumer.pay_tribute(neighbor.id, tribute_amt):
                            neighbor.receive_tribute(consumer.id, tribute_amt)
                            self.total_tributes_paid += tribute_amt
                            break

            elif consumer.social_class == "high" and consumer.budget > 180.0:
                # Seek a poor neighbor and offer some charity to build prestige
                for neighbor_id in consumer.neighbors:
                    neighbor = next((c for c in self.consumers if c.id == neighbor_id), None)
                    if neighbor and neighbor.social_class == "low" and neighbor.budget < 40.0:
                        charity_amt = consumer.budget * self.tribute_rate
                        if consumer.pay_charity(neighbor, charity_amt):
                            self.total_charity_paid += charity_amt
                            break

    def _handle_debt_repayment_or_default(self, tick: int) -> None:
        """Handles debt servicing, default triggers, and trust collapses."""
        for consumer in self.consumers:
            if consumer.debts:
                # Consumer attempts to pay some of their debt
                creditor_ids = list(consumer.debts.keys())
                for creditor_id in creditor_ids:
                    # Let's say they try to pay up to 10% of their debt per tick to maintain credibility
                    target_payment = consumer.debts[creditor_id] * 0.1
                    if target_payment > 0:
                        paid = consumer.pay_debt(creditor_id, target_payment)
                        if paid > 0:
                            # Notify creditor (could be producer or other agent)
                            producer = next((p for p in self.producers if p.id == creditor_id), None)
                            if producer:
                                producer.collect_debt(consumer.id, paid)

                # If social peace is low (trust collapse / credit squeeze) and they are heavily indebted, default
                if self.social_peace < 0.4 and sum(consumer.debts.values()) > consumer.budget * 0.8:
                    defaulted_amt = consumer.trigger_default()
                    self.total_defaults_count += 1
                    self.total_defaulted_losses += defaulted_amt

                    # Write off debt on the producers side
                    for producer in self.producers:
                        if consumer.id in producer.credits_extended:
                            producer.write_off_debt(consumer.id)

            elif consumer.is_bankrupt and self.social_peace > 0.6:
                # Can recover from bankruptcy if overall social peace restores
                consumer.recover_from_bankruptcy()

    def stop(self) -> None:
        self._running = False

    def get_agent_states(self) -> List[Dict[str, Any]]:
        states = [p.to_dict() for p in self.producers]
        states.extend(c.to_dict() for c in self.consumers)
        return states

    def get_summary(self) -> Dict[str, Any]:
        market_stats = self.market.get_statistics()
        summary = {
            "ticks": self._ticks_executed,
            "consumers": len(self.consumers),
            "producers": len(self.producers),
            "network_edges": self.social_graph.edge_count(),
            "network_density": round(self.social_graph.density(), 4),
            "avg_clustering": round(self.social_graph.avg_clustering(), 4),
            "market": market_stats,
            "events_total": self.event_bus.get_event_count(),
            "transactions_total": self.event_bus.get_event_count("Transaction"),
        }
        if self.graeber_active:
            summary.update({
                "graeber_active": True,
                "social_peace_final": round(self.social_peace, 3),
                "total_mutual_aid_count": self.total_mutual_aid_count,
                "total_mutual_aid_volume": round(self.total_mutual_aid_volume, 2),
                "total_tributes_paid": round(self.total_tributes_paid, 2),
                "total_charity_paid": round(self.total_charity_paid, 2),
                "total_credit_sales_volume": round(self.total_credit_sales_volume, 2),
                "total_defaults_count": self.total_defaults_count,
                "total_defaulted_losses": round(self.total_defaulted_losses, 2),
            })
        else:
            summary["graeber_active"] = False
        return summary
