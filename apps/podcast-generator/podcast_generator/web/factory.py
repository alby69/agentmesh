from __future__ import annotations


from fastapi import FastAPI

from podcast_generator.config import Settings
from podcast_generator.web.db import init_db
from podcast_generator.web.auth import init_oauth
from podcast_generator.agents.manager import get_agents
from podcast_generator.scheduler import MeshScheduler

def create_app(cfg: Settings) -> FastAPI:
    from podcast_generator.web.app import app as fastapi_app

    # We use a wrapper or just configure the existing app instance
    # since it's already defined in app.py.
    # Ideally, app.py should not instantiate FastAPI globally.

    return fastapi_app

async def start_services(cfg: Settings):
    init_db()
    (cfg.output_dir / "daily").mkdir(parents=True, exist_ok=True)
    (cfg.output_dir / "weekly").mkdir(parents=True, exist_ok=True)
    init_oauth(cfg)

    # Initialize Agents
    agents = get_agents(cfg)
    await agents.start()

    # Initialize Scheduler
    scheduler = MeshScheduler(cfg)
    await scheduler.start()

    return agents, scheduler
