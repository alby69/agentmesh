from pathlib import Path
from pydub import AudioSegment


def check_duration(audio_path: Path, max_minutes: int) -> tuple[float, bool]:
    """Verifica che il file audio non superi la durata massima."""
    audio = AudioSegment.from_file(audio_path)
    duration_min = len(audio) / (1000 * 60)
    return duration_min, duration_min <= max_minutes


def add_intro_outro(
    audio_path: Path, intro_path: Path | None, outro_path: Path | None, output_path: Path
):
    """Aggiunge sigla iniziale e finale."""
    audio = AudioSegment.from_file(audio_path)

    if intro_path and intro_path.exists():
        intro = AudioSegment.from_file(intro_path)
        audio = intro + audio

    if outro_path and outro_path.exists():
        outro = AudioSegment.from_file(outro_path)
        audio = audio + outro

    audio.export(output_path, format="mp3")


def merge_audio_files(paths: list[Path], output_path: Path):
    """Unisce più file audio in uno solo."""
    combined = AudioSegment.empty()
    for p in paths:
        combined += AudioSegment.from_file(p)
    combined.export(output_path, format="mp3")
