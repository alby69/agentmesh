import time
from typing import Dict, Any
from threading import Lock

class MetricsCollector:
    """
    A simple metrics collector for AgentMesh nodes.
    """
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._lock = Lock()

    def increment(self, name: str, value: int = 1):
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float):
        with self._lock:
            self._gauges[name] = value

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "counters": self._counters.copy(),
                "gauges": self._gauges.copy(),
                "timestamp": time.time()
            }

# Global metrics collector
metrics = MetricsCollector()
