"""Voice assistant API routes powered by Sarvam AI."""
import asyncio
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.core import settings
from app.services.sarvam_service import (
    NoSpeechDetectedError,
    SarvamAPIError,
    sarvam_service,
)

logger = logging.getLogger(__name__)
voice_router = APIRouter(prefix="/api/voice", tags=["voice"])

ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/m4a",
}


@voice_router.post("/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    language_code: str = Form(default="unknown"),
):
    """Convert a browser recording to text."""
    media_type = (audio.content_type or "").split(";", 1)[0].lower()
    if media_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio format.")

    content = await audio.read(settings.max_audio_upload_bytes + 1)
    if len(content) > settings.max_audio_upload_bytes:
        raise HTTPException(status_code=413, detail="Audio recording is too large.")

    try:
        transcript = await asyncio.to_thread(
            sarvam_service.transcribe,
            content,
            audio.filename or "recording.webm",
            media_type,
            language_code,
        )
        return {"transcript": transcript}
    except EnvironmentError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except NoSpeechDetectedError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except SarvamAPIError as error:
        logger.error("Sarvam transcription rejected request: %s", error)
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:
        logger.exception("Voice transcription failed")
        raise HTTPException(status_code=502, detail="Voice transcription failed.") from error


@voice_router.post("/synthesize")
async def synthesize_voice(
    text: str = Form(...),
    target_language_code: str = Form(default="en-IN"),
):
    """Convert an assistant response to playable audio."""
    text = text.strip()
    if not text or len(text) > settings.max_message_length:
        raise HTTPException(status_code=400, detail="Text must be between 1 and 500 characters.")

    try:
        audio, media_type = await asyncio.to_thread(
            sarvam_service.synthesize, text, target_language_code
        )
        return Response(content=audio, media_type=media_type)
    except EnvironmentError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Voice synthesis failed")
        raise HTTPException(status_code=502, detail="Voice synthesis failed.") from error