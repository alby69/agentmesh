"""CLI entry point for podcast-generator."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from podcast_generator.config import Settings
from podcast_generator.exceptions import ConfigError


def _get_cfg() -> Settings:
    cfg = Settings()
    cfg.validate()
    return cfg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="podcast-generator",
        description="Genera episodi podcast da newsletter (configurabile via .env)",
    )
    sub = parser.add_subparsers(dest="command")

    # daily
    p_daily = sub.add_parser("daily", help="Episodio giornaliero: ultima newsletter → traduzione → audio")
    p_daily.add_argument("--search/--no-search", dest="use_web_search", default=None,
                         help="Abilita/disabilita Google Search grounding")

    # weekly
    p_weekly = sub.add_parser("weekly", help="Episodio settimanale: aggrega N newsletter → traduzione → audio")
    p_weekly.add_argument("--days", "-d", type=int, default=7, help="Numero giorni da aggregare")
    p_weekly.add_argument("--search/--no-search", dest="use_web_search", default=None,
                          help="Abilita/disabilita Google Search grounding")

    # fetch-all
    p_fetch = sub.add_parser("fetch-all", help="Scarica tutte le newsletter non ancora processate")
    p_fetch.add_argument("--limit", "-l", type=int, default=None,
                         help="Limite massimo newsletter da processare")
    p_fetch.add_argument("--search/--no-search", dest="use_web_search", default=None,
                         help="Abilita/disabilita Google Search grounding")

    # status
    sub.add_parser("status", help="Mostra lo stato del tracker")

    # v3-generate
    sub.add_parser("v3-generate", help="V3 PoC: Fetch → ContentAgent → IPFS → Nostr")

    # server
    p_server = sub.add_parser("server", help="Avvia la Web UI server")
    p_server.add_argument("--port", type=int, default=8000, help="Porta (default: 8000)")
    p_server.add_argument("--host", type=str, default="0.0.0.0", help="Host (default: 0.0.0.0)")

    return parser


def cmd_daily(args):
    from podcast_generator.pipeline import daily_episode
    cfg = _get_cfg()
    if args.use_web_search is not None:
        cfg.use_web_search = args.use_web_search
    path = asyncio.run(daily_episode(cfg))
    print(f"Episodio salvato in: {path}")


def cmd_weekly(args):
    from podcast_generator.pipeline import weekly_episode
    cfg = _get_cfg()
    if args.use_web_search is not None:
        cfg.use_web_search = args.use_web_search
    path = asyncio.run(weekly_episode(cfg, args.days))
    print(f"Episodio salvato in: {path}")


def cmd_fetch_all(args):
    from podcast_generator.pipeline import process_all
    cfg = _get_cfg()
    if args.use_web_search is not None:
        cfg.use_web_search = args.use_web_search
    result = asyncio.run(process_all(cfg, limit=args.limit))
    print(f"Fatto: {len(result['daily'])} giornaliere, {len(result['weekly'])} settimanali")


def cmd_status(args):
    from podcast_generator.tracker import Tracker
    cfg = _get_cfg()
    tracker = Tracker(cfg.output_dir)
    total = len(tracker.data["processed"])
    by_week = tracker.get_by_week()
    print(f"\nTracker: {cfg.output_dir / '.processed.json'}")
    print(f"Puntate processate: {total}")
    print(f"Settimane coperte: {len(by_week)}")
    for wk in sorted(by_week):
        print(f"  {wk}: {len(by_week[wk])} puntate")


def cmd_v3_generate(args):
    from podcast_generator.agents.content_agent import ContentAgent
    from podcast_generator.agents.storage_agent import StorageAgent
    from podcast_generator.agents.network_agent import NetworkAgent

    async def run_v3():
        cfg = _get_cfg()
        content_agent = ContentAgent(cfg)
        storage_agent = StorageAgent(cfg)
        network_agent = NetworkAgent(cfg)

        await content_agent.start()
        await storage_agent.start()
        await network_agent.start()

        try:
            print("V3 Flow: Fetching latest newsletter...")
            nl = await content_agent.fetch_latest()

            print(f"V3 Flow: Generating episode for '{nl.title}'...")
            episode = await content_agent.generate_episode_from_newsletter(nl)

            print("V3 Flow: Uploading to IPFS...")
            cid = await storage_agent.upload_file(episode.audio_path)

            if cid:
                print(f"V3 Flow: IPFS CID: {cid}")
                print("V3 Flow: Publishing to Nostr...")
                event_id = await network_agent.publish_podcast(episode.title, cid, {})
                if event_id:
                    print("V3 Flow COMPLETE!")
                    print(f"Nostr Event ID: {event_id.to_bech32()}")
                    print(f"IPFS Gateway: {await storage_agent.get_file_url(cid)}")
        finally:
            await content_agent.stop()
            await storage_agent.stop()
            await network_agent.stop()

    asyncio.run(run_v3())


def cmd_server(args):
    import uvicorn
    from podcast_generator.web.app import app

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


COMMANDS = {
    "daily": cmd_daily,
    "weekly": cmd_weekly,
    "fetch-all": cmd_fetch_all,
    "status": cmd_status,
    "v3-generate": cmd_v3_generate,
    "server": cmd_server,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        COMMANDS[args.command](args)
    except ConfigError as e:
        print(f"Errore: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
