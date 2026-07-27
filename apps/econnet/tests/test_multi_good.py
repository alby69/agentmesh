from econnet.simulation.engine import SimulationEngine

def test_multi_good_setup_and_matching():
    engine = SimulationEngine(seed=42)
    engine.setup(
        num_consumers=10,
        num_producers=3,
        consumer_budget=100.0,
        initial_price=10.0,
        network_type="small-world",
        num_products=2
    )

    assert len(engine.products) == 2
    assert engine.products[0].id == 0
    assert engine.products[1].id == 1

    # Verify consumer has needs and reference prices initialized for both products
    for c in engine.consumers:
        assert 0 in c.needs_level_by_product
        assert 1 in c.needs_level_by_product
        assert 0 in c.reference_price_by_product
        assert 1 in c.reference_price_by_product

    # Verify producer has prices and stocks for both products
    for p in engine.producers:
        assert 0 in p.stocks_by_product
        assert 1 in p.stocks_by_product
        assert 0 in p.prices_by_product
        assert 1 in p.prices_by_product

    # Execute a step
    tick_log = engine.run(max_ticks=2)
    assert len(tick_log) == 2

    # Confirm per-product metrics populated
    assert 0 in engine.market.price_history_by_product
    assert 1 in engine.market.price_history_by_product
    assert len(engine.market.price_history_by_product[0]) == 2
    assert len(engine.market.price_history_by_product[1]) == 2
