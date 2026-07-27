import random
import math
from typing import Any, Dict, List, Optional, Tuple

from econnet.agents.base import BaseEconAgent


class QLearner:
    def __init__(self, lr: float = 0.1, discount: float = 0.9, epsilon: float = 0.1):
        self.lr = lr
        self.discount = discount
        self.epsilon = epsilon
        self.q_table: Dict[Tuple[int, int, int, int], Dict[int, float]] = {}

    def _discretize(self, state: List[float]) -> Tuple[int, int, int, int]:
        # state: [price, budget, satisfaction, social_pressure]
        price, budget, satisfaction, social_pressure = state

        p_bin = min(4, max(0, int(price / 4.0)))
        b_bin = min(4, max(0, int(budget / 30.0)))
        s_bin = min(4, max(0, int(satisfaction * 5.0)))
        sp_bin = min(4, max(0, int(social_pressure * 5.0)))

        return (p_bin, b_bin, s_bin, sp_bin)

    def choose_action(self, state: List[float], actions_available: List[int]) -> int:
        disc_state = self._discretize(state)
        if disc_state not in self.q_table:
            self.q_table[disc_state] = {a: 0.0 for a in actions_available}

        if random.random() < self.epsilon:
            return random.choice(actions_available)

        q_vals = self.q_table[disc_state]
        max_val = max(q_vals.values())
        best_actions = [a for a, v in q_vals.items() if v == max_val]
        return random.choice(best_actions)

    def update(self, state: List[float], action: int, reward: float, next_state: List[float], actions_available: List[int]) -> None:
        disc_state = self._discretize(state)
        disc_next_state = self._discretize(next_state)

        if disc_state not in self.q_table:
            self.q_table[disc_state] = {a: 0.0 for a in actions_available}
        if disc_next_state not in self.q_table:
            self.q_table[disc_next_state] = {a: 0.0 for a in actions_available}

        max_next_q = max(self.q_table[disc_next_state].values())
        old_q = self.q_table[disc_state][action]
        self.q_table[disc_state][action] = old_q + self.lr * (reward + self.discount * max_next_q - old_q)


class ConsumerAgent(BaseEconAgent):
    def __init__(
        self,
        agent_id: int,
        budget: float = 100.0,
        risk_aversion: float = 0.5,
        social_susceptibility: float = 0.5,
        anchoring: float = 0.3,
        use_rl: bool = True,
    ):
        super().__init__(agent_id, budget)
        self.risk_aversion = max(0.0, min(1.0, risk_aversion))
        self.social_susceptibility = max(0.0, min(1.0, social_susceptibility))
        self.anchoring = max(0.0, min(1.0, anchoring))
        self.use_rl = use_rl

        # Emotional state: [satisfaction, fear, enthusiasm, imitation]
        self.emotional_state = [0.5, 0.1, 0.3, 0.2]
        self.needs_level = random.uniform(0.3, 0.8)
        self.last_purchase_price: Optional[float] = None
        self.reference_price = 0.0
        self.neighbors: List[int] = []

        # Q-Learner instance
        self.q_learner = QLearner()

        # Graeberian concepts attributes
        self.social_class = "medium"
        self.debts: Dict[int, float] = {}     # agent_id -> amount owed
        self.credits: Dict[int, float] = {}   # agent_id -> amount owed to us
        self.tribute_precedents: Dict[int, float] = {}  # superior_id -> amount expected
        self.charity_precedents: Dict[int, float] = {}  # inferior_id -> amount expected
        self.communist_gifts_given = 0
        self.communist_gifts_received = 0
        self.charity_received = 0.0
        self.charity_given = 0.0
        self.tributes_paid = 0.0
        self.tributes_received = 0.0
        self.defaults_count = 0
        self.is_bankrupt = False
        self.update_social_class()

    def update_social_class(self) -> None:
        if self.budget < 60.0:
            self.social_class = "low"
        elif self.budget <= 150.0:
            self.social_class = "medium"
        else:
            self.social_class = "high"

    def step(self, tick: int, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        current_price = market_state.get("current_price", 10.0)
        avg_neighbor_satisfaction = market_state.get("avg_neighbor_satisfaction", 0.5)

        # Update social class dynamically based on current budget
        self.update_social_class()

        self._update_emotions(current_price, avg_neighbor_satisfaction)

        buy_threshold = self._compute_buy_threshold(current_price)
        willingness = self._compute_willingness(current_price, avg_neighbor_satisfaction)

        graeber_active = market_state.get("graeber", False)
        social_peace = market_state.get("social_peace", 1.0)

        can_buy = False
        use_credit = False
        quantity = 0

        if self.use_rl:
            # RL-based Decision Making
            # State: [price, budget, satisfaction, social_pressure]
            social_pressure = self.emotional_state[3] * avg_neighbor_satisfaction
            state = [current_price, self.budget, self.emotional_state[0], social_pressure]

            actions_available = [0, 1, 2]
            action_chosen = self.q_learner.choose_action(state, actions_available)

            if action_chosen > 0:
                if current_price * action_chosen <= self.budget:
                    can_buy = True
                    quantity = action_chosen
                elif graeber_active and social_peace > 0.4 and not self.is_bankrupt:
                    can_buy = True
                    use_credit = True
                    quantity = action_chosen
            else:
                quantity = 0

            self.last_state = state
            self.last_action = action_chosen
        else:
            if willingness > buy_threshold:
                if current_price <= self.budget * 0.4:
                    can_buy = True
                elif graeber_active and social_peace > 0.4 and not self.is_bankrupt:
                    # Can buy on credit if trust is high and not currently bankrupt/defaulted
                    can_buy = True
                    use_credit = True

            if can_buy:
                quantity = self._decide_quantity(current_price, willingness)
            else:
                quantity = 0

        if can_buy and quantity > 0:
            action = {
                "type": "buy",
                "agent_id": self.id,
                "tick": tick,
                "price": current_price,
                "quantity": quantity,
                "willingness": round(willingness, 3),
                "emotional_state": list(self.emotional_state),
                "use_credit": use_credit,
            }
            actions.append(action)

        self._update_needs(tick)

        if self.use_rl and hasattr(self, 'last_state'):
            new_social_pressure = self.emotional_state[3] * avg_neighbor_satisfaction
            next_state = [current_price, self.budget, self.emotional_state[0], new_social_pressure]
            debt_penalty = min(1.0, sum(self.debts.values()) / 200.0) if self.debts else 0.0
            reward = self.emotional_state[0] - debt_penalty

            self.q_learner.update(self.last_state, self.last_action, reward, next_state, [0, 1, 2])

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

        # High debts make consumer anxious and less willing to buy
        debt_pressure = min(0.3, sum(self.debts.values()) / 200.0) if self.debts else 0.0

        return max(0.0, need_factor + satisfaction_factor + enthusiasm_factor + imitation_factor + price_pressure - debt_pressure)

    def _decide_quantity(self, price: float, willingness: float) -> int:
        max_affordable = int(self.budget * 0.3 / price) if price > 0 else 0
        if max_affordable == 0 and price > 0:
            max_affordable = 1 if willingness > 0.6 else 0

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

    # Graeberian behavioral methods

    def receive_communist_gift(self, amount: float) -> None:
        self.earn(amount)
        self.communist_gifts_received += 1
        self.emotional_state[0] = min(1.0, self.emotional_state[0] + 0.25)
        self.emotional_state[1] = max(0.0, self.emotional_state[1] - 0.20)

    def give_communist_gift(self, neighbor: 'ConsumerAgent', amount: float) -> bool:
        if self.spend(amount):
            neighbor.receive_communist_gift(amount)
            self.communist_gifts_given += 1
            self.emotional_state[0] = min(1.0, self.emotional_state[0] + 0.15)
            self.emotional_state[1] = max(0.0, self.emotional_state[1] - 0.10)
            return True
        return False

    def pay_tribute(self, superior_id: int, amount: float) -> bool:
        if self.spend(amount):
            self.tributes_paid += amount
            self.tribute_precedents[superior_id] = amount
            self.emotional_state[0] = max(0.0, self.emotional_state[0] - 0.05)
            return True
        return False

    def receive_tribute(self, inferior_id: int, amount: float) -> None:
        self.earn(amount)
        self.tributes_received += amount
        self.emotional_state[2] = min(1.0, self.emotional_state[2] + 0.10)

    def pay_charity(self, inferior: 'ConsumerAgent', amount: float) -> bool:
        if self.spend(amount):
            self.charity_given += amount
            inferior.receive_charity(self.id, amount)
            self.charity_precedents[inferior.id] = amount
            self.emotional_state[0] = min(1.0, self.emotional_state[0] + 0.10)
            self.emotional_state[2] = min(1.0, self.emotional_state[2] + 0.15)
            return True
        return False

    def receive_charity(self, superior_id: int, amount: float) -> None:
        self.earn(amount)
        self.charity_received += amount
        self.charity_precedents[superior_id] = amount
        self.emotional_state[0] = min(1.0, self.emotional_state[0] + 0.20)
        self.emotional_state[1] = max(0.0, self.emotional_state[1] - 0.15)

    def incur_debt(self, creditor_id: int, amount: float) -> None:
        self.debts[creditor_id] = self.debts.get(creditor_id, 0.0) + amount
        self.emotional_state[1] = min(1.0, self.emotional_state[1] + 0.10 * (amount / 50.0))

    def pay_debt(self, creditor_id: int, amount: float) -> float:
        owed = self.debts.get(creditor_id, 0.0)
        if owed <= 0:
            return 0.0
        pay_amount = min(amount, owed, self.budget)
        if pay_amount > 0 and self.spend(pay_amount):
            self.debts[creditor_id] -= pay_amount
            if self.debts[creditor_id] <= 0.01:
                del self.debts[creditor_id]
            self.emotional_state[1] = max(0.0, self.emotional_state[1] - 0.15)
            return pay_amount
        return 0.0

    def trigger_default(self) -> float:
        """Defaults on all outstanding debts. Returns total defaulted amount."""
        total_defaulted = sum(self.debts.values())
        self.debts.clear()
        self.defaults_count += 1
        self.is_bankrupt = True
        self.emotional_state[0] = 0.0
        self.emotional_state[1] = 1.0
        self.emotional_state[2] = 0.0
        return total_defaulted

    def recover_from_bankruptcy(self) -> None:
        self.is_bankrupt = False

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "type": "consumer",
            "emotional_state": [round(x, 3) for x in self.emotional_state],
            "needs_level": round(self.needs_level, 3),
            "reference_price": round(self.reference_price, 2),
            "risk_aversion": self.risk_aversion,
            "social_susceptibility": self.social_susceptibility,
            # Graeberian extension attributes
            "social_class": self.social_class,
            "total_debts": round(sum(self.debts.values()), 2),
            "communist_gifts_given": self.communist_gifts_given,
            "communist_gifts_received": self.communist_gifts_received,
            "charity_received": round(self.charity_received, 2),
            "charity_given": round(self.charity_given, 2),
            "tributes_paid": round(self.tributes_paid, 2),
            "defaults_count": self.defaults_count,
            "is_bankrupt": self.is_bankrupt,
        })
        return d
