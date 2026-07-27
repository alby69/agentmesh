import random
from typing import Any, Dict, List

from econnet.agents.base import BaseEconAgent

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


if HAS_TORCH:
    class DemandForecaster(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(3, 8),
                nn.ReLU(),
                nn.Linear(8, 1)
            )
            self.optimizer = optim.SGD(self.parameters(), lr=0.01)
            self.criterion = nn.MSELoss()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

        def predict_demand_torch(self, price: float, volume: float, emotion: float) -> float:
            self.eval()
            with torch.no_grad():
                inp = torch.tensor([[price, volume, emotion]], dtype=torch.float32)
                out = self.forward(inp)
                return max(0.0, float(out.item()))

        def update_torch(self, price: float, volume: float, emotion: float, actual_demand: float) -> float:
            self.train()
            self.optimizer.zero_grad()
            inp = torch.tensor([[price, volume, emotion]], dtype=torch.float32)
            target = torch.tensor([[actual_demand]], dtype=torch.float32)
            pred = self.forward(inp)
            loss = self.criterion(pred, target)
            loss.backward()
            self.optimizer.step()
            return float(loss.item())
else:
    class DemandForecaster:
        def __init__(self):
            pass
        def predict_demand_torch(self, price: float, volume: float, emotion: float) -> float:
            return 0.0
        def update_torch(self, price: float, volume: float, emotion: float, actual_demand: float) -> float:
            return 0.0


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

        # ML Demand Forecaster instance
        self.forecaster = DemandForecaster()

        # Graeberian concepts attributes
        self.credits_extended: Dict[int, float] = {}  # consumer_id -> amount owed to us
        self.total_defaulted_losses = 0.0

    def step(self, tick: int, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        total_demand = market_state.get("total_demand", 0)
        competitor_avg_price = market_state.get("competitor_avg_price", self.price)
        recent_volume = market_state.get("recent_volume", 0.0)
        avg_emotion = market_state.get("avg_emotion", 0.5)

        self._produce()
        self._record_demand(total_demand)
        self._update_demand_forecast(self.price, recent_volume, avg_emotion)
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

    def _update_demand_forecast(self, current_price: float = 10.0, recent_volume: float = 0.0, avg_emotion: float = 0.5) -> None:
        if HAS_TORCH and len(self.demand_history) >= 2:
            last_demand = self.demand_history[-1]
            self.forecaster.update_torch(current_price, recent_volume, avg_emotion, last_demand)
            self.predicted_demand = self.forecaster.predict_demand_torch(current_price, recent_volume, avg_emotion)
        else:
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

        # High outstanding bad debt causes producers to raise prices to cover losses (risk premium)
        unpaid_credit = sum(self.credits_extended.values())
        if unpaid_credit > 100.0:
            risk_premium = min(0.3, unpaid_credit / 1000.0)
            self.price *= (1 + risk_premium)

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

    # Graeberian methods

    def sell_on_credit(self, consumer_id: int, quantity: int, price: float) -> float:
        actual = min(quantity, self.stock)
        if actual <= 0:
            return 0.0
        amount_owed = actual * price
        self.stock -= actual
        self.credits_extended[consumer_id] = self.credits_extended.get(consumer_id, 0.0) + amount_owed
        self.sales_history.append(actual)
        # We don't earn cash immediately, but we record the sale and potential revenue
        return amount_owed

    def collect_debt(self, consumer_id: int, amount: float) -> None:
        if consumer_id in self.credits_extended:
            self.credits_extended[consumer_id] -= amount
            if self.credits_extended[consumer_id] <= 0.01:
                del self.credits_extended[consumer_id]
            self.earn(amount)

    def write_off_debt(self, consumer_id: int) -> None:
        if consumer_id in self.credits_extended:
            loss = self.credits_extended[consumer_id]
            self.total_defaulted_losses += loss
            del self.credits_extended[consumer_id]

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "type": "producer",
            "price": self.price,
            "stock": self.stock,
            "cost_per_unit": self.cost_per_unit,
            "predicted_demand": round(self.predicted_demand, 2),
            "production_rate": self.production_rate,
            # Graeberian properties
            "credits_extended": round(sum(self.credits_extended.values()), 2),
            "total_defaulted_losses": round(self.total_defaulted_losses, 2),
        })
        return d
