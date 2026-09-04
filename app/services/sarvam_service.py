"""Sarvam AI speech-to-text and text-to-speech service."""
import base64
import os

import httpx


SARVAM_API_URL = "https://api.sarvam.ai"
DEFAULT_STT_MODEL = ""
DEFAULT_TTS_MODEL = "bulbul:v2"


class NoSpeechDetectedError(RuntimeError):
    """Raised when Sarvam receives audio but detects no speech."""


class SarvamAPIError(RuntimeError):
    """Raised when Sarvam rejects an API request."""


class SarvamService:
    """Small HTTP client for Sarvam's speech APIs."""

    def _headers(self) -> dict[str, str]:
        api_key = os.getenv("SARVAM_API_KEY")
        if not api_key:
            raise EnvironmentError("SARVAM_API_KEY is not configured.")
        return {"api-subscription-key": api_key}

    def transcribe(
        self,
        audio: bytes,
        filename: str,
        content_type: str,
        language_code: str = "unknown",
    ) -> str:
        """Transcribe an audio recording into text."""
        files = {"file": (filename, audio, content_type)}
        model = os.getenv("SARVAM_STT_MODEL", DEFAULT_STT_MODEL)
        data = {"language_code": language_code}
        if model:
            data["model"] = model
        if model == "saaras:v3":
            data["mode"] = "transcribe"
        response = httpx.post(
            f"{SARVAM_API_URL}/speech-to-text",
            headers=self._headers(),
            files=files,
            data=data,
            timeout=60.0,
        )
        if response.is_error:
            detail = response.text[:500] or response.reason_phrase
            raise SarvamAPIError(
                f"Sarvam STT request failed ({response.status_code}): {detail}"
            )
        result = response.json()
        transcript = (result.get("transcript") or "").strip()
        if not transcript:
            raise NoSpeechDetectedError(
                "No speech was detected. Please speak clearly and try again."
            )
        return transcript

    def synthesize(
        self,
        text: str,
        target_language_code: str = "en-IN",
    ) -> tuple[bytes, str]:
        """Synthesize text and return decoded audio plus its media type."""
        payload = {
            "inputs": [text],
            "target_language_code": target_language_code,
            "speaker": os.getenv("SARVAM_TTS_SPEAKER", "anushka"),
            "model": os.getenv("SARVAM_TTS_MODEL", DEFAULT_TTS_MODEL),
            "enable_preprocessing": True,
        }
        response = httpx.post(
            f"{SARVAM_API_URL}/text-to-speech",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        audio_base64 = (response.json().get("audios") or [""])[0]
        if not audio_base64:
            raise RuntimeError("Sarvam returned no synthesized audio.")
        return base64.b64decode(audio_base64), "audio/wav"


sarvam_service = SarvamService()