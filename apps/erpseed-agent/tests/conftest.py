"""Shared test fixtures for erpseed-agent tests."""

from __future__ import annotations

import os
import pytest


@pytest.fixture(autouse=True)
def _test_env(tmp_path):
    """Set a temp DB path for every test and clean up after."""
    db_path = str(tmp_path / "test_erpseed_agent.db")
    os.environ["ERPSEED_AGENT_DB_PATH"] = db_path
    yield
    os.environ.pop("ERPSEED_AGENT_DB_PATH", None)
