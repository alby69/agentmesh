import pytest
from econnet.agents.consumer import ConsumerAgent
from econnet.agents.producer import ProducerAgent
from econnet.simulation.engine import SimulationEngine


def test_graeber_consumer_attributes():
    consumer = ConsumerAgent(agent_id=10, budget=40.0)
    assert consumer.social_class == "low"

    consumer.earn(100.0)
    consumer.update_social_class()
    assert consumer.social_class == "medium"

    consumer.earn(100.0)
    consumer.update_social_class()
    assert consumer.social_class == "high"


def test_baseline_communism_gifts():
    giver = ConsumerAgent(agent_id=1, budget=200.0)
    receiver = ConsumerAgent(agent_id=2, budget=20.0)

    assert receiver.communist_gifts_received == 0
    assert giver.communist_gifts_given == 0

    success = giver.give_communist_gift(receiver, 15.0)
    assert success is True
    assert receiver.budget == 35.0
    assert receiver.communist_gifts_received == 1
    assert giver.communist_gifts_given == 1


def test_hierarchy_tributes_and_charity():
    superior = ConsumerAgent(agent_id=1, budget=300.0)
    inferior = ConsumerAgent(agent_id=2, budget=30.0)

    # Pay tribute
    success = inferior.pay_tribute(superior.id, 5.0)
    assert success is True
    assert inferior.tributes_paid == 5.0
    assert superior.tribute_precedents == {}  # Precedent is tracked on payer side
    assert inferior.tribute_precedents[superior.id] == 5.0

    # Pay charity
    success = superior.pay_charity(inferior, 25.0)
    assert success is True
    assert superior.charity_given == 25.0
    assert inferior.charity_received == 25.0
    assert superior.charity_precedents[inferior.id] == 25.0


def test_debt_and_default():
    consumer = ConsumerAgent(agent_id=3, budget=50.0)
    producer = ProducerAgent(agent_id=1, budget=500.0)

    # Incur debt
    consumer.incur_debt(producer.id, 40.0)
    producer.credits_extended[consumer.id] = 40.0
    assert consumer.debts[producer.id] == 40.0

    # Pay debt
    paid = consumer.pay_debt(producer.id, 10.0)
    producer.collect_debt(consumer.id, paid)
    assert paid == 10.0
    assert consumer.debts[producer.id] == 30.0
    assert producer.credits_extended[consumer.id] == 30.0

    # Default
    defaulted_amt = consumer.trigger_default()
    assert defaulted_amt == 30.0
    assert len(consumer.debts) == 0
    assert consumer.is_bankrupt is True
    assert consumer.defaults_count == 1


def test_simulation_engine_graeber_flow():
    config = {
        "graeber": True,
        "initial_peace": 1.0,
        "tribute_rate": 0.05,
    }
    engine = SimulationEngine(config=config, seed=42)
    engine.setup(num_consumers=15, num_producers=3, network_type="random")

    tick_log = engine.run(max_ticks=5)
    assert len(tick_log) == 5

    summary = engine.get_summary()
    assert summary["graeber_active"] is True
    assert "total_mutual_aid_count" in summary
    assert "social_peace_final" in summary
