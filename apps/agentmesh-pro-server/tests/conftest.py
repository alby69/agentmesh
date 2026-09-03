"""Test configuration for apps/agentmesh-pro-server."""

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8000")
