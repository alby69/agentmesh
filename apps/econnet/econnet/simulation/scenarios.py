from typing import Any, Dict
from econnet.simulation.engine import SimulationEngine


class ScenarioManager:
    @staticmethod
    def get_available_scenarios() -> list[str]:
        return ["Bolla 2008", "Crisi pandemia", "Boom tecnologico"]

    @staticmethod
    def apply_scenario(engine: SimulationEngine, scenario_name: str) -> None:
        """
        Configures and sets up the SimulationEngine with parameters matching the given scenario.
        """
        if scenario_name == "Bolla 2008":
            # High initial budgets, low risk aversion, scale-free network topology, Graeberian credit enabled
            engine.config.update({
                "graeber": True,
                "initial_peace": 0.9,
                "tribute_rate": 0.08,
                "use_rl": True
            })
            engine.setup(
                num_consumers=100,
                num_producers=10,
                consumer_budget=250.0,  # High liquidity
                producer_budget=1000.0,
                initial_price=12.0,
                network_type="scale-free",  # Fast bubble/contagion propagation
            )
            # Modify consumer specific attributes to reflect low risk aversion
            for c in engine.consumers:
                c.risk_aversion = 0.15  # Extremely risk-seeking / bubble behavior
                c.social_susceptibility = 0.9  # Highly susceptible to herd behavior
                c.emotional_state = [0.8, 0.0, 0.9, 0.8]  # High excitement, no fear, high imitation

        elif scenario_name == "Crisi pandemia":
            # Low initial budgets, high risk aversion, small-world network topology, low social peace
            engine.config.update({
                "graeber": True,
                "initial_peace": 0.4,  # Trust is already low / credit squeeze
                "tribute_rate": 0.02,
                "use_rl": True
            })
            engine.setup(
                num_consumers=100,
                num_producers=10,
                consumer_budget=40.0,  # Low liquidity / demand shock
                producer_budget=300.0,
                initial_price=8.0,
                network_type="small-world",
            )
            for c in engine.consumers:
                c.risk_aversion = 0.85  # Highly risk-averse
                c.social_susceptibility = 0.4
                c.emotional_state = [0.1, 0.8, 0.0, 0.2]  # High fear, low excitement

        elif scenario_name == "Boom tecnologico":
            # High producer budgets/production rates, dropping prices, highly enthusiastic consumers
            engine.config.update({
                "graeber": False,  # Pure cash market, stable growth
                "use_rl": True
            })
            engine.setup(
                num_consumers=100,
                num_producers=10,
                consumer_budget=120.0,
                producer_budget=1500.0,
                initial_price=15.0,
                network_type="random",
            )
            for p in engine.producers:
                p.production_rate = 25  # High production capacity
                p.cost_per_unit = 2.0  # Dropping cost of tech units
                p.price = 6.0
            for c in engine.consumers:
                c.risk_aversion = 0.3
                c.emotional_state = [0.9, 0.0, 0.9, 0.5]  # Very high excitement and satisfaction

        else:
            raise ValueError(f"Unknown scenario preset: {scenario_name}")
