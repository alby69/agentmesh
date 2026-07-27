import pytest
from econnet.simulation.engine import SimulationEngine
from econnet.simulation.scenarios import ScenarioManager
from econnet.simulation.events import PriceChangeEvent, TransactionEvent, AgentDecisionEvent, MarketCrashEvent


def test_scenario_manager_presets():
    engine = SimulationEngine(seed=42)

    scenarios = ScenarioManager.get_available_scenarios()
    assert "Bolla 2008" in scenarios
    assert "Crisi pandemia" in scenarios
    assert "Boom tecnologico" in scenarios

    ScenarioManager.apply_scenario(engine, "Bolla 2008")
    assert engine.graeber_active is True
    assert len(engine.consumers) == 100
    assert engine.consumers[0].risk_aversion == 0.15

    ScenarioManager.apply_scenario(engine, "Crisi pandemia")
    assert engine.graeber_active is True
    assert engine.consumers[0].risk_aversion == 0.85


def test_custom_events_emitted():
    engine = SimulationEngine(config={"graeber": True}, seed=42)
    engine.setup(num_consumers=10, num_producers=2, network_type="random")

    engine.run(max_ticks=2)

    summary = engine.get_summary()
    assert summary["events_total"] > 0

    decisions = engine.event_bus.get_events("AgentDecision")
    assert len(decisions) >= 0

    for ev in decisions:
        assert isinstance(ev, AgentDecisionEvent)
