"""Web route tests for motedico."""

import pytest
from fastapi.testclient import TestClient

from motedico.web.app import app
from motedico.web.db import init_db


@pytest.fixture(name="client")
def client_fixture():
    init_db()
    return TestClient(app)


def test_index(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "MoTeDico" in response.text
