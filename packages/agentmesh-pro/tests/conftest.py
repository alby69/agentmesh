"""Test configuration and fixtures for packages/agentmesh-pro."""

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
