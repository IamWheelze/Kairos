from __future__ import annotations

import asyncio
from typing import Optional

from google.cloud import speech_v1p1beta1 as speech


MIME_TO_ENCODING = {
    "audio/webm": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
    "audio/ogg": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    "audio/ogg;codecs=opus": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    "audio/wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
    "audio/x-wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
    "audio/l16": speech.RecognitionConfig.AudioEncoding.LINEAR16,
}


class GoogleSpeech:
    def __init__(self, language_code: str = "en-US") -> None:
        self.client = speech.SpeechClient()
        self.language = language_code

    async def recognize_bytes(self, audio_bytes: bytes, mime_type: str) -> str:
        return await asyncio.get_event_loop().run_in_executor(None, self._recognize_sync, audio_bytes, mime_type)

    def _recognize_sync(self, audio_bytes: bytes, mime_type: str) -> str:
        encoding = MIME_TO_ENCODING.get(mime_type, speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=encoding,
            language_code=self.language,
            enable_automatic_punctuation=True,
            audio_channel_count=2,
            model="default",
        )
        response = self.client.recognize(config=config, audio=audio)
        texts = [alt.transcript for res in response.results for alt in res.alternatives if alt.transcript]
        return texts[0] if texts else ""

