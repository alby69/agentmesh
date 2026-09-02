"""CLI entry point for erpseed-agent."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure root directory is in sys.path
_APP_ROOT = Path(__file__).resolve().parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("erpseed-agent")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="erpseed-agent",
        description="ERPSeed Builder Agent for AgentMesh - Enterprise Resource Planning and dynamic low-code ERP integration.",
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Start the web UI dashboard server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the web server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for the web server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--sync-capabilities",
        action="store_true",
        help="Fetch and synchronize capabilities manifest from ERPSEED backend",
    )
    return parser


async def run_server(host: str, port: int) -> None:
    import uvicorn
    from erpseed_agent.web.app import app

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def sync_capabilities_once() -> None:
    from erpseed_agent.config import get_settings
    from erpseed_agent.agents.erp_agent import ERPSeedAgent
    from erpseed_agent.web.db import init_db

    init_db()
    settings = get_settings()
    agent = ERPSeedAgent(config=settings)
    synced = await agent.sync_capabilities()
    logger.info(f"Successfully synchronized {len(synced)} capabilities from ERPSEED backend.")
    await agent.stop()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.sync_capabilities:
        asyncio.run(sync_capabilities_once())
    elif args.server:
        asyncio.run(run_server(args.host, args.port))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
