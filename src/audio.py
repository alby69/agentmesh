from pathlib import Path

from pydub import AudioSegment


def check_duration(
    audio_path: str | Path, max_minutes: int = 60
) -> tuple[float, bool]:
    audio = AudioSegment.from_mp3(str(audio_path))
    duration_minutes = len(audio) / 1000 / 60
    return duration_minutes, duration_minutes <= max_minutes


def add_intro_outro(
    audio_path: str | Path,
    intro_path: str | Path | None = None,
    outro_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    audio = AudioSegment.from_mp3(str(audio_path))

    if intro_path and Path(intro_path).exists():
        intro = AudioSegment.from_mp3(str(intro_path))
        audio = intro + audio

    if outro_path and Path(outro_path).exists():
        outro = AudioSegment.from_mp3(str(outro_path))
        audio = audio + outro

    output_path = Path(output_path or audio_path)
    audio.export(str(output_path), format="mp3")
    return output_path


def merge_audio_files(
    files: list[Path], output_path: str | Path
) -> Path:
    combined = AudioSegment.empty()
    for f in files:
        combined += AudioSegment.from_mp3(str(f))
    output_path = Path(output_path)
    combined.export(str(output_path), format="mp3")
    return output_path
