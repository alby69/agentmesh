from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict


@dataclass
class Event:
    event_type: str
    tick: int
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PriceChangeEvent(Event):
    def __init__(self, tick: int, price: float, old_price: float, agent_id: Optional[int] = None):
        super().__init__("PriceChange", tick, {
            "price": price,
            "old_price": old_price,
            "agent_id": agent_id
        })


@dataclass
class TransactionEvent(Event):
    def __init__(self, tick: int, buyer_id: int, seller_id: int, price: float, quantity: int, amount: float, use_credit: bool = False):
        super().__init__("Transaction", tick, {
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "price": price,
            "quantity": quantity,
            "amount": amount,
            "use_credit": use_credit
        })


@dataclass
class AgentDecisionEvent(Event):
    def __init__(self, tick: int, agent_id: int, agent_type: str, decision: str, details: Dict[str, Any]):
        super().__init__("AgentDecision", tick, {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "decision": decision,
            "details": details
        })


@dataclass
class MarketCrashEvent(Event):
    def __init__(self, tick: int, return_rate: float, current_price: float):
        super().__init__("MarketCrash", tick, {
            "return_rate": return_rate,
            "current_price": current_price
        })


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[Event] = []

    def on(self, event_type: str, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def emit(self, event: Event) -> None:
        self._event_log.append(event)
        for handler in self._handlers.get(event.event_type, []):
            handler(event)
        for handler in self._handlers.get("*", []):
            handler(event)

    def get_events(self, event_type: Optional[str] = None, tick: Optional[int] = None) -> List[Event]:
        events = self._event_log
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        if tick is not None:
            events = [e for e in events if e.tick == tick]
        return events

    def get_event_count(self, event_type: Optional[str] = None) -> int:
        if event_type is None:
            return len(self._event_log)
        return len([e for e in self._event_log if e.event_type == event_type])

    def clear(self) -> None:
        self._event_log.clear()
