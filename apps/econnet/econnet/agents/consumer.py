import random
import math
from typing import Any, Dict, List, Optional

from econnet.agents.base import BaseEconAgent


class ConsumerAgent(BaseEconAgent):
    def __init__(
        self,
        agent_id: int,
        budget: float = 100.0,
        risk_aversion: float = 0.5,
        social_susceptibility: float = 0.5,
        anchoring: float = 0.3,
    ):
        super().__init__(agent_id, budget)
        self.risk_aversion = max(0.0, min(1.0, risk_aversion))
        self.social_susceptibility = max(0.0, min(1.0, social_susceptibility))
        self.anchoring = max(0.0, min(1.0, anchoring))

        # Emotional state: [satisfaction, fear, enthusiasm, imitation]
        self.emotional_state = [0.5, 0.1, 0.3, 0.2]
        self.needs_level = random.uniform(0.3, 0.8)
        self.last_purchase_price: Optional[float] = None
        self.reference_price = 0.0
        self.neighbors: List[int] = []

    def step(self, tick: int, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        current_price = market_state.get("current_price", 10.0)
        avg_neighbor_satisfaction = market_state.get("avg_neighbor_satisfaction", 0.5)

        self._update_emotions(current_price, avg_neighbor_satisfaction)

        buy_threshold = self._compute_buy_threshold(current_price)
        willingness = self._compute_willingness(current_price, avg_neighbor_satisfaction)

        if willingness > buy_threshold and current_price <= self.budget * 0.4:
            quantity = self._decide_quantity(current_price, willingness)
            action = {
                "type": "buy",
                "agent_id": self.id,
                "tick": tick,
                "price": current_price,
                "quantity": quantity,
                "willingness": round(willingness, 3),
                "emotional_state": list(self.emotional_state),
            }
            actions.append(action)

        self._update_needs(tick)
        self.record_state(tick)
        return actions

    def _update_emotions(self, price: float, neighbor_satisfaction: float) -> None:
        if self.reference_price > 0:
            price_ratio = price / self.reference_price
        else:
            price_ratio = 1.0
            self.reference_price = price

        if price_ratio < 0.9:
            self.emotional_state[0] = min(1.0, self.emotional_state[0] + 0.05)
            self.emotional_state[2] = min(1.0, self.emotional_state[2] + 0.08)
        elif price_ratio > 1.1:
            self.emotional_state[1] = min(1.0, self.emotional_state[1] + 0.07)
            self.emotional_state[0] = max(0.0, self.emotional_state[0] - 0.03)

        if neighbor_satisfaction > 0.6:
            self.emotional_state[3] = min(1.0, self.emotional_state[3] + 0.04 * self.social_susceptibility)
        elif neighbor_satisfaction < 0.4:
            self.emotional_state[3] = max(0.0, self.emotional_state[3] - 0.02)

        for i in range(4):
            self.emotional_state[i] *= 0.95
            self.emotional_state[i] = max(0.0, min(1.0, self.emotional_state[i]))

    def _compute_buy_threshold(self, price: float) -> float:
        base = 0.3 + self.risk_aversion * 0.3
        if self.last_purchase_price and price < self.last_purchase_price:
            base -= 0.1 * self.anchoring
        elif self.last_purchase_price and price > self.last_purchase_price:
            base += 0.15 * self.anchoring
        return max(0.1, min(0.9, base))

    def _compute_willingness(self, price: float, neighbor_satisfaction: float) -> float:
        need_factor = self.needs_level * 0.4
        satisfaction_factor = self.emotional_state[0] * 0.2
        enthusiasm_factor = self.emotional_state[2] * 0.15
        imitation_factor = self.emotional_state[3] * neighbor_satisfaction * 0.15

        price_pressure = 0.0
        if self.reference_price > 0:
            price_pressure = max(0, (self.reference_price - price) / self.reference_price) * 0.1

        return need_factor + satisfaction_factor + enthusiasm_factor + imitation_factor + price_pressure

    def _decide_quantity(self, price: float, willingness: float) -> int:
        max_affordable = int(self.budget * 0.3 / price) if price > 0 else 0
        desire = math.ceil(willingness * 3)
        if max_affordable > 0:
            return min(desire, max(max_affordable, 1))
        return 0

    def _update_needs(self, tick: int) -> None:
        decay = 0.005 * (1.0 - self.risk_aversion * 0.5)
        self.needs_level = min(1.0, self.needs_level + decay)

    def on_purchase(self, price: float, quantity: int) -> None:
        self.last_purchase_price = price
        if self.reference_price == 0:
            self.reference_price = price
        else:
            self.reference_price = 0.8 * self.reference_price + 0.2 * price
        self.needs_level = max(0.0, self.needs_level - 0.1 * quantity)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "type": "consumer",
            "emotional_state": [round(x, 3) for x in self.emotional_state],
            "needs_level": round(self.needs_level, 3),
            "reference_price": round(self.reference_price, 2),
            "risk_aversion": self.risk_aversion,
            "social_susceptibility": self.social_susceptibility,
        })
        return d
