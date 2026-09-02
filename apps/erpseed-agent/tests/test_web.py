"""Web route tests for erpseed-agent dashboard."""

import pytest
from fastapi.testclient import TestClient

from erpseed_agent.web.app import app
from erpseed_agent.web.db import init_db


@pytest.fixture(name="client")
def client_fixture():
    init_db()
    with TestClient(app) as client:
        yield client


def test_index_route(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "ERPSeed Agent" in response.text
    assert "Dashboard" in response.text


def test_health_route(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["agent_id"] == "erpseed-builder-agent"


def test_builder_routes(client: TestClient):
    res = client.get("/builder")
    assert res.status_code == 200
    assert "AI Low-Code Builder Interface" in res.text

    res_post = client.post(
        "/builder/generate",
        data={"type": "model", "model_name": "client_order", "description": "Client order tracking model"},
    )
    assert res_post.status_code == 200
    assert "client_order" in res_post.text


def test_modules_route(client: TestClient):
    res = client.get("/modules")
    assert res.status_code == 200
    assert "ERPSEED Modules" in res.text
    assert "sales" in res.text
    assert "fattura_elettronica" in res.text


def test_invoices_route(client: TestClient):
    res = client.get("/invoices")
    assert res.status_code == 200
    assert "Electronic Invoices" in res.text


def test_workflows_route(client: TestClient):
    res = client.get("/workflows")
    assert res.status_code == 200
    assert "Workflows" in res.text


def test_mesh_route(client: TestClient):
    res = client.get("/mesh")
    assert res.status_code == 200
    assert "Nostr A2A Mesh Network" in res.text


def test_vault_route(client: TestClient):
    res = client.get("/vault")
    assert res.status_code == 200
    assert "IPFS Vault Storage" in res.text


def test_tenants_routes(client: TestClient):
    # 1. Get tenants page
    res_get = client.get("/tenants")
    assert res_get.status_code == 200
    assert "Tenant Mappings" in res_get.text

    # 2. Add tenant mapping
    res_add = client.post(
        "/tenants/add",
        data={"npub": "npub1testuser", "tenant_id": 99, "api_key": "secret123"},
        follow_redirects=True,
    )
    assert res_add.status_code == 200
    assert "npub1testuser" in res_add.text
    assert "Tenant #99" in res_add.text

    # 3. Delete tenant mapping
    res_del = client.post(
        "/tenants/delete",
        data={"npub": "npub1testuser"},
        follow_redirects=True,
    )
    assert res_del.status_code == 200
    assert "npub1testuser" not in res_del.text


def test_capabilities_routes(client: TestClient):
    res_get = client.get("/capabilities")
    assert res_get.status_code == 200
    assert "Capabilities" in res_get.text


def test_logs_route(client: TestClient):
    res_get = client.get("/logs")
    assert res_get.status_code == 200
    assert "Execution Logs" in res_get.text
