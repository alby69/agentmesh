import pytest
import os
from econnet.web.db import EconNetDB

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_econnet.db"
    db = EconNetDB(db_path=str(db_file))
    yield db
    db.close()

def test_db_init_and_save(temp_db):
    sim_id = "test-sim-123"
    scenario = "Test Scenario"
    ticks_count = 5
    final_price = 12.50
    gini_index = 0.25
    graeber_active = True

    tick_log = [
        {"tick": 0, "price": 10.0, "volume": 5, "gini_index": 0.22, "herd_effect": 0.1, "sentiment_propagation": 0.2, "social_peace": 1.0, "total_debt": 0.0, "defaults_count": 0},
        {"tick": 1, "price": 11.0, "volume": 7, "gini_index": 0.23, "herd_effect": 0.15, "sentiment_propagation": 0.25, "social_peace": 0.95, "total_debt": 10.0, "defaults_count": 0}
    ]

    agent_states = [
        {"id": 1, "type": "consumer", "budget": 95.0, "social_class": "medium", "is_bankrupt": False},
        {"id": 2, "type": "producer", "budget": 505.0, "social_class": "high", "is_bankrupt": False}
    ]

    transactions = [
        {"tick": 1, "buyer_id": 1, "seller_id": 2, "price": 11.0, "quantity": 1, "use_credit": False}
    ]

    # Save to temp_db
    temp_db.save_simulation_run(
        sim_id=sim_id,
        scenario=scenario,
        ticks_count=ticks_count,
        final_price=final_price,
        gini_index=gini_index,
        graeber_active=graeber_active,
        tick_log=tick_log,
        agent_states=agent_states,
        transactions_log=transactions
    )

    # Check simulations saved
    sims = temp_db.get_past_simulations()
    assert len(sims) == 1
    assert sims[0]["id"] == sim_id
    assert sims[0]["scenario"] == scenario
    assert sims[0]["ticks"] == ticks_count
    assert sims[0]["final_price"] == final_price
    assert sims[0]["gini_index"] == gini_index
    assert sims[0]["graeber_active"] == 1

    # Check ticks saved
    ticks = temp_db.get_simulation_ticks(sim_id)
    assert len(ticks) == 2
    assert ticks[0]["tick"] == 0
    assert ticks[0]["price"] == 10.0
    assert ticks[1]["tick"] == 1
    assert ticks[1]["price"] == 11.0
    assert ticks[1]["total_debt"] == 10.0

    # Delete simulation
    temp_db.delete_simulation(sim_id)
    sims_after = temp_db.get_past_simulations()
    assert len(sims_after) == 0
