import json
import threading
import time
from typing import Optional

from websocket import create_connection, WebSocket

from kairos_core.config import get_settings


class ProPresenterClient:
    """ProPresenter 7 Remote WebSocket client (basic subset).

    Notes:
    - Connects to ws://{host}:{port}/remote
    - Authenticates with password if set
    - Sends simple control actions (best-effort; exact action names may vary by version)
    - Provides basic retry on send if connection dropped
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._ws: Optional[WebSocket] = None
        self._lock = threading.Lock()
        self._connected = False
        self._last_error: Optional[str] = None
        self._protocol = "701"  # API protocol version; adjust if needed per PP version

    # ------------- public -------------
    def status(self) -> dict:
        return {
            "connected": self._connected,
            "last_error": self._last_error,
            "host": self.settings.propresenter_host,
            "port": self.settings.propresenter_port,
        }

    async def next_slide(self) -> bool:
        return await self._send_action({"action": "presentationTriggerNext"})

    async def previous_slide(self) -> bool:
        return await self._send_action({"action": "presentationTriggerPrevious"})

    async def clear_screen(self) -> bool:
        # Clear all layers (adjust to clear only text if desired)
        return await self._send_action({"action": "clearAll"})

    async def clear_text_layer(self) -> bool:
        return await self._send_action({"action": "clearText"})

    async def goto_song(self, identifier: str) -> bool:
        # Trigger first slide of a presentation by path/name identifier
        payload = {
            "action": "presentationTriggerIndex",
            "presentationPath": identifier,
            "slideIndex": 0,
        }
        return await self._send_action(payload)

    async def goto_section(self, section: str) -> bool:
        # Attempt to trigger by group/section name (may vary by PP version)
        payload = {"action": "presentationTriggerGroup", "groupName": section}
        return await self._send_action(payload)

    async def play_pause_media(self) -> bool:
        return await self._send_action({"action": "mediaPlayPause"})

    # ------------- internals -------------
    def _connect_blocking(self) -> None:
        url = f"ws://{self.settings.propresenter_host}:{self.settings.propresenter_port}/remote"
        try:
            ws = create_connection(url, timeout=3)
            # Authenticate (password may be empty)
            auth_msg = {
                "action": "authenticate",
                "protocol": self._protocol,
                "password": self.settings.propresenter_password or "",
                "deviceName": "Kairos",
                "application": "remote",
            }
            ws.send(json.dumps(auth_msg))
            # Consume one or two initial frames if any (non-blocking)
            ws.settimeout(0.2)
            try:
                _ = ws.recv()
            except Exception:
                pass
            self._ws = ws
            self._connected = True
            self._last_error = None
        except Exception as e:
            self._connected = False
            self._ws = None
            self._last_error = str(e)

    def _ensure_connected(self) -> bool:
        if self._connected and self._ws is not None:
            return True
        with self._lock:
            if self._connected and self._ws is not None:
                return True
            self._connect_blocking()
            return self._connected

    async def _send_action(self, payload: dict) -> bool:
        # Run sync send in a thread to avoid blocking event loop
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._send_action_sync, payload)

    def _send_action_sync(self, payload: dict) -> bool:
        try:
            if not self._ensure_connected():
                return False
            assert self._ws is not None
            self._ws.send(json.dumps(payload))
            # Optional: wait briefly for ack without blocking too long
            self._ws.settimeout(0.2)
            try:
                _ = self._ws.recv()
            except Exception:
                pass
            return True
        except Exception as e:
            # Try one reconnect + resend
            self._connected = False
            self._last_error = str(e)
            try:
                self._connect_blocking()
                if self._connected and self._ws is not None:
                    self._ws.send(json.dumps(payload))
                    return True
            except Exception as e2:
                self._connected = False
                self._last_error = str(e2)
            return False
