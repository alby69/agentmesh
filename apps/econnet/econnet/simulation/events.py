from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict


@dataclass
class Event:
    event_type: str
    tick: int
    data: Dict[str, Any] = field(default_factory=dict)


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
