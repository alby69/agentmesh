from econnet.agents.consumer import ConsumerAgent
from econnet.agents.producer import ProducerAgent
from econnet.network.social_graph import SocialGraph
from econnet.simulation.market import Market
from econnet.simulation.engine import SimulationEngine


def test_consumer_step():
    consumer = ConsumerAgent(agent_id=0, budget=100.0, risk_aversion=0.5)
    market_state = {"current_price": 5.0, "avg_neighbor_satisfaction": 0.6}
    actions = consumer.step(tick=1, market_state=market_state)
    assert isinstance(actions, list)
    assert consumer.needs_level >= 0.0


def test_consumer_emotional_state():
    consumer = ConsumerAgent(agent_id=0, budget=100.0)
    assert len(consumer.emotional_state) == 4
    for val in consumer.emotional_state:
        assert 0.0 <= val <= 1.0


def test_producer_step():
    producer = ProducerAgent(agent_id=0, budget=500.0, initial_stock=50, price=10.0)
    market_state = {"total_demand": 20, "competitor_avg_price": 12.0}
    actions = producer.step(tick=1, market_state=market_state)
    assert isinstance(actions, list)
    assert producer.stock >= 0


def test_producer_pricing():
    producer = ProducerAgent(agent_id=0, cost_per_unit=5.0, price=10.0)
    initial_price = producer.price
    for i in range(20):
        producer._record_demand(50)
        producer._update_demand_forecast()
        producer._adjust_price(competitor_avg_price=10.0)
    assert producer.price != initial_price


def test_market_order_matching():
    market = Market()
    market.submit_buy(agent_id=0, price=10.0, quantity=5, tick=0)
    market.submit_sell(agent_id=1, price=8.0, quantity=5, tick=0)
    transactions = market.match_orders(tick=0)
    assert len(transactions) == 1
    assert transactions[0].quantity == 5
    assert 8.0 <= transactions[0].price <= 10.0


def test_market_no_match():
    market = Market()
    market.submit_buy(agent_id=0, price=5.0, quantity=5, tick=0)
    market.submit_sell(agent_id=1, price=10.0, quantity=5, tick=0)
    transactions = market.match_orders(tick=0)
    assert len(transactions) == 0


def test_social_graph():
    graph = SocialGraph(seed=42)
    ids = list(range(20))
    graph.build_small_world(ids, k=4, p=0.1)
    assert graph.node_count() == 20
    assert graph.edge_count() > 0
    neighbors = graph.get_neighbors(0)
    assert isinstance(neighbors, list)


def test_social_graph_evolve():
    graph = SocialGraph(seed=42)
    ids = list(range(20))
    graph.build_random(ids, edge_probability=0.2)
    initial_edges = graph.edge_count()
    graph.evolve(creation_rate=1.0, removal_rate=0.0)
    assert graph.edge_count() >= initial_edges


def test_simulation_engine():
    engine = SimulationEngine(seed=42)
    engine.setup(num_consumers=20, num_producers=5, network_type="small-world")
    tick_log = engine.run(max_ticks=10)
    assert len(tick_log) == 10
    assert tick_log[0]["price"] > 0


def test_simulation_summary():
    engine = SimulationEngine(seed=42)
    engine.setup(num_consumers=10, num_producers=3)
    engine.run(max_ticks=5)
    summary = engine.get_summary()
    assert summary["ticks"] == 5
    assert summary["consumers"] == 10
    assert summary["producers"] == 3
