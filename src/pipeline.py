import asyncio
import re
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from src.config import Config
from src.audio import check_duration, merge_audio_files
from src.fetcher import (
    fetch_latest_newsletter,
    fetch_multiple_newsletters,
    fetch_all_newsletters,
)
from src.translator import translate_newsletter, translate_multiple
from src.tts import generate_audio
from src.tracker import Tracker

console = Console()


def _slugify(text: str, max_len: int = 50) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:max_len]


def _save_script(script: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8")


def daily_episode(cfg: Config) -> Path:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[yellow]Estrazione newsletter...", total=None
        )
        newsletter = asyncio.run(
            fetch_latest_newsletter(
                cfg.archive_url,
                load_more_selector=cfg.load_more_selector,
                link_pattern=cfg.link_pattern,
            )
        )
        progress.update(task, description="[yellow]Traduzione con Gemini...")
        script = translate_newsletter(
            cfg.gemini_api_key,
            cfg.gemini_model,
            newsletter.content,
        )
        progress.update(task, description="[yellow]Generazione audio ElevenLabs...")
        date_str = newsletter.date.strftime("%Y-%m-%d")
        slug = _slugify(newsletter.title)
        daily_dir = cfg.output_dir / "daily"
        audio_path = daily_dir / f"{date_str}_{slug}.mp3"
        script_path = daily_dir / f"{date_str}_{slug}.txt"
        generate_audio(
            cfg.elevenlabs_api_key,
            script,
            cfg.elevenlabs_voice_id,
            audio_path,
        )
        _save_script(script, script_path)
        Tracker(cfg.output_dir).mark_processed(
            newsletter.url, newsletter.title, date_str,
            str(audio_path), str(script_path),
        )
        duration, ok = check_duration(audio_path, cfg.max_episode_minutes)
        progress.update(
            task,
            description="[green]Fatto!",
        )

    console.print(f"\n[bold green]Episodio creato:[/] {audio_path}")
    console.print(f"[bold]Durata:[/] {duration:.1f} minuti")
    if not ok:
        console.print(
            f"[yellow]Attenzione:[/] supera il limite di {cfg.max_episode_minutes} min"
        )
    return audio_path


def weekly_episode(cfg: Config, days: int = 7) -> Path:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"[yellow]Estrazione ultime {days} newsletter...", total=None
        )
        newsletters = asyncio.run(
            fetch_multiple_newsletters(
                cfg.archive_url, days,
                load_more_selector=cfg.load_more_selector,
                link_pattern=cfg.link_pattern,
            )
        )
        progress.update(
            task, description="[yellow]Unione e traduzione con Gemini..."
        )
        newsletter_items = [(n.title, n.content) for n in newsletters]
        script = translate_multiple(
            cfg.gemini_api_key, cfg.gemini_model, newsletter_items
        )
        progress.update(task, description="[yellow]Generazione audio ElevenLabs...")
        today = datetime.now()
        iso = today.isocalendar()
        week_label = f"{iso[0]}-W{iso[1]:02d}"
        weekly_dir = cfg.output_dir / "weekly"
        audio_path = weekly_dir / f"{week_label}.mp3"
        script_path = weekly_dir / f"{week_label}.txt"
        generate_audio(
            cfg.elevenlabs_api_key,
            script,
            cfg.elevenlabs_voice_id,
            audio_path,
        )
        _save_script(script, script_path)
        duration, ok = check_duration(audio_path, cfg.max_episode_minutes)
        progress.update(
            task,
            description="[green]Fatto!",
        )

    console.print(f"\n[bold green]Episodio settimanale creato:[/] {audio_path}")
    console.print(f"[bold]Durata:[/] {duration:.1f} minuti")
    if not ok:
        console.print(
            f"[yellow]Attenzione:[/] supera il limite di {cfg.max_episode_minutes} min"
        )
    return audio_path


def _generate_weekly_compilations(
    cfg: Config, tracker: Tracker
) -> list[Path]:
    weekly_dir = cfg.output_dir / "weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    weekly_paths: list[Path] = []

    for week_key, items in sorted(tracker.get_by_week().items()):
        weekly_audio = weekly_dir / f"{week_key}.mp3"
        if weekly_audio.exists():
            continue

        daily_audios: list[Path] = []
        for it in items:
            p = Path(it["daily_file"])
            if p.exists():
                daily_audios.append(p)

        if len(daily_audios) < 2:
            continue

        console.print(f"  [cyan]Unisco {len(daily_audios)} puntate per {week_key}...[/]")
        merge_audio_files(daily_audios, weekly_audio)
        weekly_paths.append(weekly_audio)

    return weekly_paths


def process_all(cfg: Config, limit: int | None = None) -> dict[str, list[Path]]:
    tracker = Tracker(cfg.output_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[yellow]Scarico tutte le newsletter dall'archivio...", total=None
        )
        newsletters = asyncio.run(
            fetch_all_newsletters(
                cfg.archive_url,
                load_more_selector=cfg.load_more_selector,
                link_pattern=cfg.link_pattern,
            )
        )
        if limit:
            newsletters = newsletters[:limit]

        unprocessed = [
            n for n in newsletters if not tracker.is_processed(n.url)
        ]

        if not unprocessed:
            progress.update(task, description="[green]Tutto già processato!")
            console.print("[yellow]Nessuna nuova newsletter da processare.[/]")
            return {"daily": [], "weekly": []}

        console.print(
            f"\n[bold]Trovate {len(unprocessed)} nuove newsletter "
            f"su {len(newsletters)} totali[/]\n"
        )

        daily_paths: list[Path] = []
        for i, nl in enumerate(unprocessed, 1):
            short = nl.title[:50]
            progress.update(
                task,
                description=f"[yellow][{i}/{len(unprocessed)}] Traduco: {short}...",
            )
            script = translate_newsletter(
                cfg.gemini_api_key, cfg.gemini_model, nl.content
            )

            date_str = nl.date.strftime("%Y-%m-%d")
            slug = _slugify(nl.title)
            daily_dir = cfg.output_dir / "daily"
            audio_path = daily_dir / f"{date_str}_{slug}.mp3"
            script_path = daily_dir / f"{date_str}_{slug}.txt"

            if audio_path.exists():
                console.print(f"  [yellow]Salto (già presente): {audio_path.name}[/]")
                tracker.mark_processed(
                    nl.url, nl.title, date_str,
                    str(audio_path), str(script_path),
                )
                daily_paths.append(audio_path)
                continue

            progress.update(
                task,
                description=f"[yellow][{i}/{len(unprocessed)}] Audio: {short}...",
            )
            generate_audio(
                cfg.elevenlabs_api_key, script,
                cfg.elevenlabs_voice_id, audio_path,
            )
            _save_script(script, script_path)
            tracker.mark_processed(
                nl.url, nl.title, date_str,
                str(audio_path), str(script_path),
            )
            daily_paths.append(audio_path)

        progress.update(
            task, description="[yellow]Generazione compilation settimanali..."
        )
        weekly_paths = _generate_weekly_compilations(cfg, tracker)
        progress.update(task, description="[green]Completato!")

    console.print(f"\n[bold green]Puntate giornaliere create:[/] {len(daily_paths)}")
    console.print(f"[bold green]Compilation settimanali create:[/] {len(weekly_paths)}")
    return {"daily": daily_paths, "weekly": weekly_paths}
