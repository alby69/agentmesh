from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import edge_tts

from podcast_generator.config import Settings
from podcast_generator.exceptions import TTSError


def get_text_hash(text: str, voice: str) -> str:
    """Generates a unique hash for a text/voice combination."""
    return hashlib.sha256(f"{voice}:{text}".encode()).hexdigest()


async def generate_audio_edge(
    text: str, voice: str, output_path: str | Path
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
    except Exception as e:
        raise TTSError(f"Edge-TTS error: {e}") from e
    return output_path


async def generate_audio_elevenlabs(
    api_key: str, text: str, voice: str, output_path: str | Path
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=300,
            )
            response.raise_for_status()
            output_path.write_bytes(response.content)
    except Exception as e:
        raise TTSError(f"ElevenLabs API error: {e}") from e
    return output_path


async def generate_audio(
    cfg: Settings,
    text: str,
    output_path: str | Path,
) -> Path:
    # Handle multi-speaker dialogue
    if cfg.podcast_format == "dialogue" and ("[Host]:" in text or "[Guest]:" in text):
        return await _generate_dialogue_audio(cfg, text, output_path)

    # Infrastructure v3.1: TTS Caching
    voice = cfg.host_voice or cfg.tts_voice
    if cfg.tts_provider == "elevenlabs" and cfg.elevenlabs_api_key:
        voice = cfg.elevenlabs_voice or voice

    text_hash = get_text_hash(text, voice)
    cache_path = cfg.output_dir / "cache" / "tts" / f"{text_hash}.mp3"

    if cache_path.exists():
        import shutil
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(cache_path, output_path)
        return Path(output_path)

    # Actual generation
    if cfg.tts_provider == "elevenlabs" and cfg.elevenlabs_api_key:
        final_path = await generate_audio_elevenlabs(
            cfg.elevenlabs_api_key, text, voice, output_path
        )
    else:
        final_path = await generate_audio_edge(text, voice, output_path)

    # Store in cache
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(final_path, cache_path)

    return final_path


async def _generate_dialogue_audio(
    cfg: Settings,
    text: str,
    output_path: str | Path,
) -> Path:
    """Parses dialogue and generates multi-speaker audio."""
    from podcast_generator.audio import merge_audio_files
    import re

    # Split text into turns
    turns = re.split(r"(\[(?:Host|Guest)\]:)", text)
    processed_turns = []
    current_speaker = "Host"

    for i in range(1, len(turns), 2):
        speaker_tag = turns[i]
        content = turns[i+1].strip()
        if not content:
            continue

        current_speaker = "Host" if "Host" in speaker_tag else "Guest"
        processed_turns.append((current_speaker, content))

    if not processed_turns:
        # Fallback to monologue if parsing fails
        cfg.podcast_format = "monologue"
        return await generate_audio(cfg, text, output_path)

    temp_paths = []
    try:
        for i, (speaker, content) in enumerate(processed_turns):
            voice = cfg.host_voice if speaker == "Host" else cfg.guest_voice
            if cfg.tts_provider == "elevenlabs" and cfg.elevenlabs_api_key:
                voice = (cfg.elevenlabs_voice if speaker == "Host"
                         else (cfg.elevenlabs_guest_voice or cfg.elevenlabs_voice))

            turn_hash = get_text_hash(content, voice)
            turn_path = cfg.output_dir / "cache" / "tts" / f"{turn_hash}.mp3"

            if not turn_path.exists():
                turn_path.parent.mkdir(parents=True, exist_ok=True)
                if cfg.tts_provider == "elevenlabs" and cfg.elevenlabs_api_key:
                    await generate_audio_elevenlabs(cfg.elevenlabs_api_key, content, voice, turn_path)
                else:
                    await generate_audio_edge(content, voice, turn_path)

            temp_paths.append(turn_path)

        # Merge all turns
        merge_audio_files(temp_paths, output_path)
    except Exception as e:
        raise TTSError(f"Dialogue synthesis error: {e}") from e

    return Path(output_path)
