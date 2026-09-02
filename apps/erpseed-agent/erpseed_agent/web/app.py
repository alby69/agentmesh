"""FastAPI web application for erpseed-agent dashboard and operator interface."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from erpseed_agent.config import get_settings, ERPSeedConfig
from erpseed_agent.agents.erp_agent import ERPSeedAgent
from erpseed_agent.web.db import (
    init_db,
    list_tenant_mappings,
    set_tenant_mapping,
    delete_tenant_mapping,
    list_cached_capabilities,
    list_agent_logs,
)

logger = logging.getLogger(__name__)

templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

_settings: ERPSeedConfig = get_settings()
_agent: Optional[ERPSeedAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _agent
    init_db()
    _agent = ERPSeedAgent(config=_settings)
    await _agent.start()
    yield
    if _agent:
        await _agent.stop()


app = FastAPI(
    title="ERPSeed Builder Agent",
    version=_settings.agent_version,
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    tenants = list_tenant_mappings()
    capabilities = list_cached_capabilities()
    logs = list_agent_logs(limit=10)
    backend_status = await _agent.bridge.health_check() if _agent else False
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "config": _settings,
            "backend_status": backend_status,
            "tenants_count": len(tenants),
            "capabilities_count": len(capabilities),
            "logs": logs,
        },
    )


@app.get("/tenants", response_class=HTMLResponse)
async def tenants_page(request: Request) -> HTMLResponse:
    tenants = list_tenant_mappings()
    return templates.TemplateResponse(
        request,
        "tenants.html",
        {
            "config": _settings,
            "tenants": tenants,
        },
    )


@app.post("/tenants/add")
async def add_tenant(
    npub: str = Form(...),
    tenant_id: int = Form(...),
    api_key: str = Form(""),
):
    set_tenant_mapping(npub=npub.strip(), tenant_id=tenant_id, api_key=api_key.strip())
    return RedirectResponse(url="/tenants", status_code=303)


@app.post("/tenants/delete")
async def remove_tenant(npub: str = Form(...)):
    delete_tenant_mapping(npub=npub.strip())
    return RedirectResponse(url="/tenants", status_code=303)


@app.get("/capabilities", response_class=HTMLResponse)
async def capabilities_page(request: Request) -> HTMLResponse:
    capabilities = list_cached_capabilities()
    return templates.TemplateResponse(
        request,
        "capabilities.html",
        {
            "config": _settings,
            "capabilities": capabilities,
        },
    )


@app.post("/capabilities/sync")
async def sync_capabilities():
    if _agent:
        synced = await _agent.sync_capabilities()
        return JSONResponse({"status": "success", "synced_count": len(synced)})
    return JSONResponse({"status": "error", "reason": "Agent not initialized"}, status_code=500)


@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request) -> HTMLResponse:
    logs = list_agent_logs(limit=100)
    return templates.TemplateResponse(
        request,
        "logs.html",
        {
            "config": _settings,
            "logs": logs,
        },
    )


@app.get("/health")
async def health_endpoint():
    backend_status = await _agent.bridge.health_check() if _agent else False
    return {
        "status": "healthy" if backend_status else "degraded",
        "agent_id": _settings.agent_id,
        "erpseed_backend_connected": backend_status,
    }
