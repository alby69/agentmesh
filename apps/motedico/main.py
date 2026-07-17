"""CLI entry point for motedico."""

from __future__ import annotations

import argparse
import asyncio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="motedico",
        description="Decentralized project collaboration and advisory mesh",
    )
    parser.add_argument(
        "--server", action="store_true",
        help="Start the web UI server",
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Port for the web server (default: 8000)",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0",
        help="Host for the web server (default: 0.0.0.0)",
    )
    return parser


async def run_server(host: str, port: int) -> None:
    import uvicorn
    from motedico.web.app import app

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.server:
        asyncio.run(run_server(args.host, args.port))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
