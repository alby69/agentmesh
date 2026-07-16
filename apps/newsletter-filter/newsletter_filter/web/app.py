import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from newsletter_filter.config import FilterSettings
from newsletter_filter.agents.filter_agent import FilterAgent, FilterAgentConfig
from newsletter_filter.engine import process_filtering
from newsletter_filter.web.db import (
    init_db, get_articles, get_article_count, save_article,
    get_db_settings, save_db_settings, save_scan_job, complete_scan_job,
    get_scan_jobs, clear_articles,
)
from agentmesh.llm.factory import LLMProviderFactory

logger = logging.getLogger("newsletter_filter.web.app")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

_scan_jobs: dict[int, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Newsletter Filter web app started.")
    yield
    for task in _scan_jobs.values():
        task.cancel()
    logger.info("Newsletter Filter web app stopped.")


app = FastAPI(
    title="Newsletter Filter",
    description="Cognitive filtering for newsletters and feeds",
    version="0.1.0",
    lifespan=lifespan,
)


def _get_settings() -> FilterSettings:
    return FilterSettings()


def _get_agent_and_settings() -> tuple[FilterAgent, FilterSettings]:
    settings = _get_settings()
    api_key = settings.llm_api_key or "mock-key"
    try:
        llm_provider = LLMProviderFactory.create(
            settings.llm_provider,
            api_key=api_key,
            default_model=settings.llm_model,
        )
    except Exception as e:
        logger.error("Failed to create LLM provider: %s", e)
        raise
    agent_config = FilterAgentConfig()
    return FilterAgent(agent_config, llm_provider), settings


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    total = get_article_count()
    relevant = get_article_count(relevant_only=True)
    articles = get_articles(limit=20)
    jobs = get_scan_jobs(limit=5)
    return templates.TemplateResponse(request, "index.html", {
        "request": request,
        "articles": articles,
        "total": total,
        "relevant": relevant,
        "jobs": jobs,
    })


@app.get("/articles", response_class=HTMLResponse)
async def articles_partial(
    request: Request,
    relevant_only: bool = Query(False),
    limit: int = Query(50),
):
    articles = get_articles(relevant_only=relevant_only, limit=limit)
    total = get_article_count()
    relevant = get_article_count(relevant_only=True)
    return templates.TemplateResponse(request, "articles_table.html", {
        "request": request,
        "articles": articles,
        "total": total,
        "relevant": relevant,
    })


@app.post("/scan")
async def trigger_scan(
    request: Request,
    source_type: str = Form("rss"),
    source: str = Form(""),
    query: str = Form(""),
):
    settings = _get_settings()
    source = source.strip()
    query = query.strip() or settings.default_query

    if not source:
        if source_type == "rss":
            source = settings.rss_urls[0] if settings.rss_urls else "https://stefanogatti.substack.com/feed"
        else:
            source = settings.imap_folder or "INBOX"

    job_id = save_scan_job(source_type, source, query)

    async def _run_scan():
        try:
            agent, _ = _get_agent_and_settings()
            imap_config = None
            if source_type == "imap":
                imap_config = {
                    "host": settings.imap_host,
                    "user": settings.imap_user,
                    "password": settings.imap_password,
                }
            results = await process_filtering(
                source_type=source_type,
                source_url_or_folder=source,
                criteria=query,
                agent=agent,
                imap_config=imap_config,
                limit=10,
            )
            for r in results:
                save_article({**r, "source_type": source_type})
            complete_scan_job(job_id, len(results), sum(1 for r in results if r.get("analysis", {}).get("relevant")))
        except Exception as e:
            logger.error("Scan job %d failed: %s", job_id, e)
            complete_scan_job(job_id, 0, 0)

    task = asyncio.create_task(_run_scan())
    _scan_jobs[job_id] = task

    return HTMLResponse(
        content=f"""
        <div hx-get="/scan-status/{job_id}" hx-trigger="every 2s" hx-target="this" hx-swap="outerHTML">
            <div class="flex items-center gap-2 text-blue-400 text-sm mt-2">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <span>Scansione in corso...</span>
            </div>
        </div>
        """
    )


@app.get("/scan-status/{job_id}", response_class=HTMLResponse)
async def scan_status(request: Request, job_id: int):
    jobs = get_scan_jobs(limit=10)
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        return HTMLResponse(content="<span class='text-gray-500'>Job non trovato.</span>")

    if job["status"] == "completed":
        articles = get_articles(limit=20)
        total = get_article_count()
        relevant = get_article_count(relevant_only=True)
        table_html = templates.TemplateResponse(request, "articles_table.html", {
            "request": request,
            "articles": articles,
            "total": total,
            "relevant": relevant,
        })
        return HTMLResponse(content=f"""
            <div class="flex items-center gap-2 text-green-400 text-sm mt-2 mb-4">
                <i class="fa-solid fa-circle-check"></i>
                <span>Scansione completata! {job['relevant_articles']} rilevanti su {job['total_articles']} articoli.</span>
            </div>
            {table_html.body.decode()}
        """)

    return HTMLResponse(content="""
        <div class="flex items-center gap-2 text-blue-400 text-sm mt-2">
            <i class="fa-solid fa-spinner fa-spin"></i>
            <span>Scansione in corso...</span>
        </div>
    """)


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    current = get_db_settings()
    return templates.TemplateResponse(request, "settings.html", {
        "request": request,
        "settings": current,
    })


@app.post("/settings")
async def save_settings(
    request: Request,
    rss_urls: str = Form(""),
    imap_host: str = Form(""),
    imap_user: str = Form(""),
    imap_password: str = Form(""),
    imap_folder: str = Form("INBOX"),
    default_query: str = Form(""),
    llm_provider: str = Form("openai"),
    llm_model: str = Form("gpt-40-mini"),
):
    settings_data = {}
    if rss_urls.strip():
        settings_data["rss_urls"] = rss_urls.strip()
    if imap_host.strip():
        settings_data["imap_host"] = imap_host.strip()
    if imap_user.strip():
        settings_data["imap_user"] = imap_user.strip()
    if imap_password.strip():
        settings_data["imap_password"] = imap_password.strip()
    if imap_folder.strip():
        settings_data["imap_folder"] = imap_folder.strip()
    if default_query.strip():
        settings_data["default_query"] = default_query.strip()
    if llm_provider.strip():
        settings_data["llm_provider"] = llm_provider.strip()
    if llm_model.strip():
        settings_data["llm_model"] = llm_model.strip()

    save_db_settings(settings_data)
    return HTMLResponse(content="""
        <div class="bg-green-500/10 border border-green-500/30 text-green-400 p-4 rounded-xl mt-4">
            Impostazioni salvate con successo!
        </div>
    """)


@app.post("/clear")
async def clear_all():
    clear_articles()
    return HTMLResponse(content="""
        <div class="bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 p-4 rounded-xl mt-4">
            Articoli cancellati.
            <div hx-get="/articles" hx-trigger="load" hx-target="#articles-table-container"></div>
        </div>
    """)


@app.get("/api/articles")
async def api_articles(
    relevant_only: bool = Query(False),
    limit: int = Query(50),
):
    return JSONResponse(content=get_articles(relevant_only=relevant_only, limit=limit))


@app.get("/api/stats")
async def api_stats():
    return JSONResponse(content={
        "total": get_article_count(),
        "relevant": get_article_count(relevant_only=True),
    })
