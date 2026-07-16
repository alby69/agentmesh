import random
from typing import Any, Dict, List

from econnet.agents.base import BaseEconAgent


class ProducerAgent(BaseEconAgent):
    def __init__(
        self,
        agent_id: int,
        budget: float = 500.0,
        cost_per_unit: float = 5.0,
        initial_stock: int = 50,
        price: float = 10.0,
        production_rate: int = 10,
    ):
        super().__init__(agent_id, budget)
        self.cost_per_unit = cost_per_unit
        self.stock = initial_stock
        self.initial_stock = initial_stock
        self.price = price
        self.production_rate = production_rate
        self.price_history: List[float] = [price]
        self.demand_history: List[float] = []
        self.sales_history: List[int] = []
        self.predicted_demand = float(production_rate)

    def step(self, tick: int, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        total_demand = market_state.get("total_demand", 0)
        competitor_avg_price = market_state.get("competitor_avg_price", self.price)

        self._produce()
        self._record_demand(total_demand)
        self._update_demand_forecast()
        self._adjust_price(competitor_avg_price)

        if self.stock > 0:
            action = {
                "type": "sell",
                "agent_id": self.id,
                "tick": tick,
                "price": self.price,
                "stock": self.stock,
                "predicted_demand": round(self.predicted_demand, 2),
            }
            actions.append(action)

        self.record_state(tick)
        return actions

    def _produce(self) -> None:
        if self.stock < self.initial_stock:
            production = min(self.production_rate, self.initial_stock - self.stock)
            cost = production * self.cost_per_unit
            if cost <= self.budget:
                self.stock += production
                self.spend(cost)

    def _record_demand(self, demand: float) -> None:
        self.demand_history.append(demand)
        if len(self.demand_history) > 50:
            self.demand_history = self.demand_history[-50:]

    def _update_demand_forecast(self) -> None:
        if len(self.demand_history) < 3:
            self.predicted_demand = sum(self.demand_history) / max(len(self.demand_history), 1)
            return

        alpha = 0.3
        ema = self.demand_history[0]
        for d in self.demand_history[1:]:
            ema = alpha * d + (1 - alpha) * ema
        self.predicted_demand = max(0, ema)

    def _adjust_price(self, competitor_avg_price: float) -> None:
        if self.predicted_demand > self.stock * 0.8:
            increase = 0.05 + random.uniform(0, 0.03)
            self.price *= (1 + increase)
        elif self.predicted_demand < self.stock * 0.3:
            decrease = 0.04 + random.uniform(0, 0.02)
            self.price *= (1 - decrease)

        min_price = self.cost_per_unit * 1.05
        max_price = self.cost_per_unit * 10
        self.price = max(min_price, min(max_price, self.price))

        if competitor_avg_price > 0:
            diff = (competitor_avg_price - self.price) / competitor_avg_price
            self.price *= (1 + diff * 0.1)

        self.price = round(self.price, 2)
        self.price_history.append(self.price)

    def sell(self, quantity: int, price: float) -> float:
        actual = min(quantity, self.stock)
        if actual <= 0:
            return 0.0
        revenue = actual * price
        self.stock -= actual
        self.earn(revenue)
        self.sales_history.append(actual)
        return revenue

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "type": "producer",
            "price": self.price,
            "stock": self.stock,
            "cost_per_unit": self.cost_per_unit,
            "predicted_demand": round(self.predicted_demand, 2),
            "production_rate": self.production_rate,
        })
        return d
