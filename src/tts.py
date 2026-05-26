from pathlib import Path
from elevenlabs import ElevenLabs
import edge_tts


async def generate_audio_elevenlabs(
    api_key: str,
    text: str,
    voice_id: str,
    output_path: str | Path,
) -> Path:
    client = ElevenLabs(api_key=api_key)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    return output_path


async def generate_audio_edge(
    text: str,
    voice: str,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    return output_path


async def generate_audio(
    text: str,
    voice: str,
    output_path: str | Path,
    elevenlabs_api_key: str | None = None,
) -> Path:
    if elevenlabs_api_key:
        return await generate_audio_elevenlabs(
            elevenlabs_api_key, text, voice, output_path
        )
    else:
        return await generate_audio_edge(text, voice, output_path)
