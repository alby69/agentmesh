from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseEconAgent(ABC):
    def __init__(self, agent_id: int, budget: float = 100.0):
        self.id = agent_id
        self.budget = budget
        self.initial_budget = budget
        self.total_spent = 0.0
        self.total_earned = 0.0
        self.history: list[Dict[str, Any]] = []

    @abstractmethod
    def step(self, tick: int, market_state: Dict[str, Any]) -> list[Dict[str, Any]]:
        ...

    def record_state(self, tick: int) -> None:
        self.history.append({
            "tick": tick,
            "budget": round(self.budget, 2),
            "total_spent": round(self.total_spent, 2),
            "total_earned": round(self.total_earned, 2),
        })

    def spend(self, amount: float) -> bool:
        if amount <= self.budget:
            self.budget -= amount
            self.total_spent += amount
            return True
        return False

    def earn(self, amount: float) -> None:
        self.budget += amount
        self.total_earned += amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "budget": round(self.budget, 2),
            "total_spent": round(self.total_spent, 2),
            "total_earned": round(self.total_earned, 2),
        }
