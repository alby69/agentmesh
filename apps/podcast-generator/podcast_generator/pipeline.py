from __future__ import annotations

from pathlib import Path
from typing import Optional

from podcast_generator.config import Settings
from podcast_generator.builder import PodcastGenerator


async def daily_episode(cfg: Settings) -> Path:
    gen = PodcastGenerator(cfg)
    print("Estrazione newsletter...")
    episode = await gen.fetch_and_build_latest()
    print(f"Episodio creato: {episode.audio_path}")
    print(f"Durata: {episode.duration_minutes:.1f} minuti")
    _warn_duration(cfg, episode)
    return episode.audio_path


async def weekly_episode(cfg: Settings, days: int = 7) -> Path:
    gen = PodcastGenerator(cfg)
    print(f"Estrazione ultime {days} newsletter...")
    episode = await gen.fetch_and_build_weekly(days)
    print(f"Episodio settimanale creato: {episode.audio_path}")
    print(f"Durata: {episode.duration_minutes:.1f} minuti")
    _warn_duration(cfg, episode)
    return episode.audio_path


async def process_all(cfg: Settings, limit: Optional[int] = None) -> dict:
    gen = PodcastGenerator(cfg)
    print("Scarico newsletter...")
    result = await gen.process_backlog(limit)

    if result["unprocessed_count"] == 0:
        print("Nessuna nuova newsletter da processare.")
        return {"daily": [], "weekly": []}

    total = result["total_count"]
    unprocessed = result["unprocessed_count"]
    print(f"Trovate {unprocessed} nuove newsletter su {total} totali")

    for i, _ in enumerate(result["daily"], 1):
        print(f"  [{i}/{unprocessed}] Audio generato")

    print("Compilation settimanali completate!")
    print(f"Puntate giornaliere create: {len(result['daily'])}")
    print(f"Compilation settimanali create: {len(result['weekly'])}")
    return {"daily": result["daily"], "weekly": result["weekly"]}


def _warn_duration(cfg: Settings, episode) -> None:
    if (
        episode.duration_minutes
        and episode.duration_minutes > cfg.max_episode_minutes
    ):
        print(f"Attenzione: supera il limite di {cfg.max_episode_minutes} min")
