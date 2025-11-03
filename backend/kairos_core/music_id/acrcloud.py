from __future__ import annotations

import base64
import hashlib
import hmac
import time
from typing import Optional

import httpx

from kairos_core.config import get_settings
from kairos_core.music_id.interfaces import MusicIDClient, MusicIDResult


class ACRCloudClient(MusicIDClient):
    """Minimal ACRCloud Identify client.

    Expects raw PCM or audio bytes; sends as base64 in request body.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        if not (self.settings.acrcloud_host and self.settings.acrcloud_key and self.settings.acrcloud_secret):
            raise RuntimeError("ACRCloud not configured")

    async def identify(self, pcm_bytes: bytes) -> MusicIDResult:
        # Construct signature per ACRCloud spec
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(int(time.time()))

        string_to_sign = "\n".join([http_method, http_uri, self.settings.acrcloud_key or "", data_type, signature_version, timestamp])
        sign = base64.b64encode(hmac.new((self.settings.acrcloud_secret or "").encode("utf-8"), string_to_sign.encode("utf-8"), digestmod=hashlib.sha1).digest()).decode("utf-8")

        data = {
            "access_key": self.settings.acrcloud_key,
            "sample_bytes": str(len(pcm_bytes)),
            "sample": base64.b64encode(pcm_bytes).decode("ascii"),
            "timestamp": timestamp,
            "signature": sign,
            "data_type": data_type,
            "signature_version": signature_version,
        }

        url = f"https://{self.settings.acrcloud_host}/v1/identify"
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(url, data=data)
            resp.raise_for_status()
            j = resp.json()

        # Parse result
        title: Optional[str] = None
        artist: Optional[str] = None
        conf: float = 0.0
        try:
            status = j.get("status", {})
            if status.get("code") == 0:
                md = j.get("metadata", {})
                mus = md.get("music", [])
                if mus:
                    top = mus[0]
                    title = top.get("title")
                    artists = top.get("artists") or []
                    if artists:
                        artist = artists[0].get("name")
                    conf = float(top.get("score", 0)) / 100.0 if isinstance(top.get("score"), (int, float)) else 0.9
        except Exception:
            pass

        return MusicIDResult(title=title, artist=artist, confidence=conf)

