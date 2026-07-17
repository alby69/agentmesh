from __future__ import annotations

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, Form, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

from newsletter_filter.config import FilterSettings
from newsletter_filter.web.db import (
    init_db, get_db_settings, save_db_settings,
    add_or_update_article, get_articles, get_connection
)
from newsletter_filter.agents.filter_agent import FilterAgent, FilterAgentConfig
from newsletter_filter.fetcher import fetch_rss, fetch_imap
from agentmesh.llm.factory import LLMProviderFactory

# Logger setup
logger = logging.getLogger("newsletter_filter.web.app")

templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

# Shared memory/state for scanning jobs
_scan_jobs: Dict[str, Dict[str, Any]] = {}


def load_effective_settings() -> FilterSettings:
    """
    Loads settings from the database if they exist, otherwise falls back to environment variables.
    """
    db_s = get_db_settings()
    if db_s:
        # Reconstruct rss_urls list from comma separated string
        rss_urls_str = db_s.get("rss_urls", "")
        rss_list = [u.strip() for u in rss_urls_str.split(",") if u.strip()] if rss_urls_str else []
        return FilterSettings(
            llm_provider=db_s.get("llm_provider") or "openai",
            llm_api_key=db_s.get("llm_api_key") or "",
            llm_model=db_s.get("llm_model") or "gpt-4o-mini",
            imap_host=db_s.get("imap_host") or "",
            imap_user=db_s.get("imap_user") or "",
            imap_password=db_s.get("imap_password") or "",
            imap_folder=db_s.get("imap_folder") or "INBOX",
            rss_urls=rss_list,
            default_query=db_s.get("default_query") or "Risorse Umane e AI"
        )
    return FilterSettings()


async def _run_scanning_background(job_id: str, source_type: str):
    """
    Asynchronous background task to fetch items, execute cognitive filtering via LLM agent,
    and save results into the SQLite database.
    """
    _scan_jobs[job_id]["status"] = "running"
    _scan_jobs[job_id]["processed"] = 0
    _scan_jobs[job_id]["total"] = 0

    try:
        settings = load_effective_settings()
        query_criteria = settings.default_query

        # 1. Fetch content items
        articles_to_process = []
        if source_type == "rss":
            urls = settings.rss_urls
            if not urls:
                # Default fallback
                urls = ["https://stefanogatti.substack.com/feed"]

            for u in urls:
                fetched = await fetch_rss(u)
                articles_to_process.extend(fetched)
        elif source_type == "imap":
            if not settings.imap_host or not settings.imap_user:
                raise ValueError("IMAP Host o Utente mancanti nelle impostazioni.")

            fetched = await fetch_imap(
                host=settings.imap_host,
                user=settings.imap_user,
                password=settings.imap_password,
                folder=settings.imap_folder or "INBOX",
                limit=10
            )
            articles_to_process.extend(fetched)
        else:
            raise ValueError(f"Sorgente non supportata: {source_type}")

        total_count = len(articles_to_process)
        _scan_jobs[job_id]["total"] = total_count
        logger.info(f"Job {job_id}: fetched {total_count} articles to analyze.")

        if total_count == 0:
            _scan_jobs[job_id]["status"] = "completed"
            return

        # 2. Setup LLM Provider and Filter Agent
        api_key = settings.llm_api_key or os.getenv("OPENAI_API_KEY") or "mock-key"
        llm_provider = LLMProviderFactory.create(
            settings.llm_provider,
            api_key=api_key,
            default_model=settings.llm_model
        )

        agent_config = FilterAgentConfig()
        agent = FilterAgent(agent_config, llm_provider)

        # 3. Analyze each item and save to Database
        for idx, item in enumerate(articles_to_process):
            try:
                analysis = await agent.filter_and_extract(
                    title=item.title,
                    content=item.content,
                    criteria=query_criteria
                )

                # Save into DB
                add_or_update_article(
                    title=item.title,
                    url=item.url,
                    content=item.content,
                    date=item.date,
                    relevant=analysis.get("relevant", False),
                    score=analysis.get("score", 0.0),
                    summary=analysis.get("summary", ""),
                    key_points=analysis.get("key_points", []),
                    justification=analysis.get("justification", "")
                )
            except Exception as item_err:
                logger.error(f"Error filtering article '{item.title}': {item_err}")

            _scan_jobs[job_id]["processed"] = idx + 1

        _scan_jobs[job_id]["status"] = "completed"
        logger.info(f"Job {job_id}: completed successfully.")

    except Exception as e:
        logger.error(f"Error in background scanning job {job_id}: {e}")
        _scan_jobs[job_id]["status"] = "failed"
        _scan_jobs[job_id]["error"] = str(e)


@asynccontextmanager
async def _lifespan(app_instance: FastAPI):
    # Initialize the SQLite Database
    init_db()
    # Save default settings if table is empty
    if not get_db_settings():
        default_s = FilterSettings()
        save_db_settings({
            "llm_provider": default_s.llm_provider,
            "llm_model": default_s.llm_model,
            "llm_api_key": default_s.llm_api_key or "",
            "imap_host": default_s.imap_host,
            "imap_user": default_s.imap_user,
            "imap_password": default_s.imap_password,
            "imap_folder": default_s.imap_folder,
            "rss_urls": ",".join(default_s.rss_urls) if default_s.rss_urls else "https://stefanogatti.substack.com/feed",
            "default_query": default_s.default_query
        })
    yield


app = FastAPI(
    title="Newsletter Filter Web App",
    description="Asynchronous Cognitive Filtering App with HTMX UI",
    version="4.0.0",
    lifespan=_lifespan
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    settings = load_effective_settings()
    return templates.TemplateResponse(
        request, "index.html", {
            "settings": settings,
            "rss_urls_list": settings.rss_urls
        }
    )


@app.get("/articles", response_class=HTMLResponse)
async def list_articles_route(
    request: Request,
    search: Optional[str] = Query(None),
    relevant_only: Optional[str] = Query(None),
    sort_by: str = Query("date")
):
    is_relevant = True if relevant_only == "true" else None
    articles = get_articles(
        relevant_only=is_relevant,
        search_query=search,
        sort_by=sort_by
    )
    return templates.TemplateResponse(
        request, "articles_list.html", {
            "articles": articles
        }
    )


@app.get("/article/{article_id}", response_class=HTMLResponse)
async def article_detail_route(request: Request, article_id: int):
    # Retrieve article from Database
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Articolo non trovato.")

        article = dict(row)
        try:
            import json
            article["key_points"] = json.loads(article["key_points"]) if article["key_points"] else []
        except Exception:
            article["key_points"] = []

    return templates.TemplateResponse(
        request, "detail_modal.html", {
            "article": article
        }
    )


@app.post("/save-settings", response_class=HTMLResponse)
async def save_settings_route(
    llm_provider: str = Form(...),
    llm_model: str = Form(...),
    llm_api_key: Optional[str] = Form(None),
    default_query: str = Form(...),
    rss_urls: str = Form(...),
    imap_host: str = Form(""),
    imap_folder: str = Form("INBOX"),
    imap_user: str = Form(""),
    imap_password: str = Form("")
):
    # Prepare dictionary for SQLite insertion
    # Clean RSS URLs list (comma separated)
    clean_urls = [u.strip() for u in rss_urls.split(",") if u.strip()]
    rss_urls_joined = ",".join(clean_urls)

    settings_dict = {
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "llm_api_key": llm_api_key or "",
        "imap_host": imap_host,
        "imap_folder": imap_folder,
        "imap_user": imap_user,
        "imap_password": imap_password,
        "rss_urls": rss_urls_joined,
        "default_query": default_query
    }

    try:
        save_db_settings(settings_dict)
        return HTMLResponse(
            content="<span class='text-green-400 font-bold'><i class='fa-solid fa-circle-check mr-1'></i> Impostazioni salvate!</span>"
        )
    except Exception as e:
        logger.error(f"Error saving DB settings: {e}")
        return HTMLResponse(
            content=f"<span class='text-red-400 font-bold'><i class='fa-solid fa-triangle-exclamation mr-1'></i> Errore: {e}</span>"
        )


@app.post("/trigger-scan", response_class=HTMLResponse)
async def trigger_scan_route(source_type: str = Form(...)):
    job_id = str(uuid.uuid4())
    _scan_jobs[job_id] = {
        "status": "pending",
        "processed": 0,
        "total": 0,
        "source_type": source_type
    }

    # Spawn background task
    asyncio.create_task(_run_scanning_background(job_id, source_type))

    # Return the HTMX polling status component
    return HTMLResponse(
        content=f"""
        <div hx-get="/check-scan-status/{job_id}" hx-trigger="every 2s" hx-swap="outerHTML"
             class="flex flex-col gap-2 text-blue-400 bg-slate-900 border border-slate-800 p-4 rounded-xl mt-4">
            <div class="flex items-center gap-3 font-semibold">
                <svg class="animate-spin h-5 w-5 text-brand-500" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <span>Avvio scansione asincrona ({source_type.upper()})...</span>
            </div>
        </div>
        """
    )


@app.get("/check-scan-status/{job_id}", response_class=HTMLResponse)
async def check_scan_status_route(job_id: str):
    job = _scan_jobs.get(job_id)
    if not job:
        return HTMLResponse("<div class='text-red-400'>Stato scansione sconosciuto o scaduto.</div>")

    status = job.get("status")
    processed = job.get("processed", 0)
    total = job.get("total", 0)
    source_type = job.get("source_type", "rss")

    if status in ("pending", "running"):
        pct = int((processed / total) * 100) if total > 0 else 0
        return HTMLResponse(
            content=f"""
            <div hx-get="/check-scan-status/{job_id}" hx-trigger="every 2s" hx-swap="outerHTML"
                 class="flex flex-col gap-2 text-blue-400 bg-slate-900 border border-slate-800 p-4 rounded-xl mt-4">
                <div class="flex items-center justify-between font-semibold text-sm">
                    <span class="flex items-center gap-2">
                        <i class="fa-solid fa-spinner animate-spin text-brand-500"></i>
                        Scansione in corso ({source_type.upper()}) - Analizzati {processed} di {total} articoli...
                    </span>
                    <span class="text-xs font-mono">{pct}%</span>
                </div>
                <div class="w-full bg-slate-950 rounded-full h-1.5 border border-slate-800 overflow-hidden">
                    <div class="bg-brand-500 h-1.5 rounded-full transition-all duration-500" style="width: {pct}%"></div>
                </div>
            </div>
            """
        )

    if status == "completed":
        # Returns a nice success notification that triggers a load of the table container!
        return HTMLResponse(
            content=f"""
            <div hx-get="/articles" hx-trigger="load" hx-target="#articles-table-container"
                 class="bg-green-500/10 border border-green-500/30 text-green-400 p-4 rounded-xl mt-4 flex justify-between items-center">
                <div class="flex items-center gap-3 font-semibold text-sm">
                    <i class="fa-solid fa-circle-check text-lg"></i>
                    <span>Scansione completata con successo! Caricamento nuovi articoli...</span>
                </div>
                <button type="button" onclick="this.parentElement.remove()" class="text-xs font-bold hover:text-white transition">Chiudi</button>
            </div>
            """
        )

    # Failed status
    err_msg = job.get("error", "Errore sconosciuto")
    return HTMLResponse(
        content=f"""
        <div class="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-xl mt-4 flex flex-col gap-1">
            <div class="flex items-center gap-3 font-semibold text-sm">
                <i class="fa-solid fa-triangle-exclamation text-lg"></i>
                <span>Errore durante la scansione:</span>
            </div>
            <p class="text-xs font-mono ml-8">{err_msg}</p>
        </div>
        """
    )


@app.post("/export-podcast", response_class=HTMLResponse)
async def export_podcast_route(request: Request):
    """
    Sends the list of checked article URLs to the Podcast Generator REST API.
    This creates an async, decoupled inter-app communication pipeline.
    """
    body = await request.json()
    urls = body.get("urls", [])

    if not urls:
        return HTMLResponse(
            content="""
            <div id="export-status" class="bg-red-500/15 border border-red-500/30 text-red-400 p-3 rounded-xl text-xs font-semibold">
                <i class="fa-solid fa-triangle-exclamation mr-1.5"></i> Nessun articolo selezionato per l'esportazione.
            </div>
            """
        )

    settings = load_effective_settings()
    podcast_url = settings.podcast_gen_url.rstrip("/")
    api_token = settings.podcast_gen_api_token

    # Target endpoint on podcast-generator
    endpoint = f"{podcast_url}/api/v1/generate"
    headers = {}
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"

    logger.info(f"Exporting {len(urls)} URLs to Podcast Generator at: {endpoint}")

    try:
        async with AsyncClient() as client:
            # Send the request to Podcast Generator with 15s timeout
            response = await client.post(
                endpoint,
                json={"urls": urls},
                headers=headers,
                timeout=15.0
            )

            if response.status_code == 200:
                resp_json = response.json()
                job_id = resp_json.get("job_id", "N/D")
                return HTMLResponse(
                    content=f"""
                    <div id="export-status" class="bg-green-500/15 border border-green-500/30 text-green-400 p-4 rounded-xl text-xs font-semibold flex flex-col gap-1">
                        <div class="flex items-center gap-1.5">
                            <i class="fa-solid fa-circle-check text-sm"></i>
                            <span>Esportato con successo a Podcast Generator!</span>
                        </div>
                        <p class="text-slate-400 font-normal mt-1">ID Lavoro Creato: <span class="font-mono text-white">{job_id}</span></p>
                        <p class="text-slate-400 font-normal">Il server sta ora sintetizzando l'audio asincronamente.</p>
                    </div>
                    """
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Server returned status {response.status_code}: {response.text}"
                )
    except Exception as e:
        logger.error(f"Failed to export articles to Podcast Generator: {e}")
        return HTMLResponse(
            content=f"""
            <div id="export-status" class="bg-red-500/15 border border-red-500/30 text-red-400 p-4 rounded-xl text-xs font-semibold flex flex-col gap-1">
                <div class="flex items-center gap-1.5">
                    <i class="fa-solid fa-circle-exclamation text-sm"></i>
                    <span>Esportazione fallita. Controlla che Podcast Generator sia attivo.</span>
                </div>
                <p class="text-slate-400 font-normal mt-1">URL di Destinazione: <span class="font-mono text-white">{endpoint}</span></p>
                <p class="text-slate-500 font-normal font-mono text-[10px]">Dettaglio errore: {e}</p>
            </div>
            """
        )
