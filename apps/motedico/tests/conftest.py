"""Shared test fixtures for motedico."""

import os

import pytest


@pytest.fixture(autouse=True)
def _test_env(tmp_path):
    """Set a temp DB for every test and clean up after."""
    db_path = str(tmp_path / "test.db")
    os.environ["MOTEDICO_DB_PATH"] = db_path
    yield
    os.environ.pop("MOTEDICO_DB_PATH", None)
