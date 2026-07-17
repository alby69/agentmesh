"""Shared test fixtures for econnet."""

import pytest


@pytest.fixture
def sim_config():
    """Default simulation config for tests."""
    return {
        "ticks": 10,
        "consumers": 5,
        "producers": 2,
        "budget": 100.0,
        "price": 10.0,
        "network_type": "random",
    }
