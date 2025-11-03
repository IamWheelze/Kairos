from typing import Callable, Optional, Literal, Dict
from pydantic import BaseModel
import sqlite3
import uuid

from kairos_core.config import get_settings
from kairos_core.content.db import get_identifier_by_title


class Intent(BaseModel):
    name: Literal[
        "NextSlide",
        "PreviousSlide",
        "ClearScreen",
        "GoToSong",
        "GoToSection",
        "PlayPauseMedia",
    ]
    params: dict | None = None
    confidence: float | None = None


class Orchestrator:
    def __init__(self, event_sink: Callable[[str], None], propresenter) -> None:
        self.emit = event_sink
        self.prop = propresenter
        self.settings = get_settings()
        self._pending: Dict[str, Intent] = {}
        self._enabled: bool = True

    async def handle_intent(self, intent: Intent, db: sqlite3.Connection) -> str:
        if not self._enabled:
            self.emit(self._json_event("info", {"msg": f"AI disabled; ignoring {intent.name}"}))
            return "disabled"
        conf = intent.confidence if intent.confidence is not None else 1.0
        if intent.name == "GoToSong":
            title = None
            if intent.params:
                title = intent.params.get("song_title") or intent.params.get("name")
            if not title:
                self.emit("HITL: Missing song title for GoToSong; no action")
                return "needs_confirmation"
            identifier = get_identifier_by_title(db, title)
            if not identifier:
                self.emit(f"HITL: Song '{title}' not found in mapping; no action")
                return "not_found"
            if conf < self.settings.nlu_confidence_threshold:
                pid = self._queue_pending("GoToSong", {"song_title": title})
                self.emit(
                    self._json_event(
                        "pending",
                        {
                            "id": pid,
                            "intent": "GoToSong",
                            "detail": f"Show '{title}'",
                        },
                    )
                )
                return "needs_confirmation"
            ok = await self.prop.goto_song(identifier)
            self.emit(f"Action: GoToSong -> {identifier} ({'ok' if ok else 'fail'})")
            return "ok" if ok else "fail"

        if intent.name == "NextSlide":
            if conf < self.settings.nlu_confidence_threshold:
                pid = self._queue_pending("NextSlide", {})
                self.emit(self._json_event("pending", {"id": pid, "intent": "NextSlide"}))
                return "needs_confirmation"
            ok = await self.prop.next_slide()
            self.emit(f"Action: NextSlide ({'ok' if ok else 'fail'})")
            return "ok" if ok else "fail"

        if intent.name == "PreviousSlide":
            if conf < self.settings.nlu_confidence_threshold:
                pid = self._queue_pending("PreviousSlide", {})
                self.emit(self._json_event("pending", {"id": pid, "intent": "PreviousSlide"}))
                return "needs_confirmation"
            ok = await self.prop.previous_slide()
            self.emit(f"Action: PreviousSlide ({'ok' if ok else 'fail'})")
            return "ok" if ok else "fail"

        if intent.name == "ClearScreen":
            if conf < self.settings.nlu_confidence_threshold:
                pid = self._queue_pending("ClearScreen", {})
                self.emit(self._json_event("pending", {"id": pid, "intent": "ClearScreen"}))
                return "needs_confirmation"
            ok = await self.prop.clear_screen()
            self.emit(f"Action: ClearScreen ({'ok' if ok else 'fail'})")
            return "ok" if ok else "fail"

        if intent.name == "GoToSection":
            section = (intent.params or {}).get("section") if intent.params else None
            if not section:
                self.emit("HITL: Missing section for GoToSection; no action")
                return "needs_confirmation"
            if conf < self.settings.nlu_confidence_threshold:
                pid = self._queue_pending("GoToSection", {"section": section})
                self.emit(self._json_event("pending", {"id": pid, "intent": "GoToSection", "detail": section}))
                return "needs_confirmation"
            ok = await self.prop.goto_section(section)
            self.emit(f"Action: GoToSection {section} ({'ok' if ok else 'fail'})")
            return "ok" if ok else "fail"

        if intent.name == "PlayPauseMedia":
            if conf < self.settings.nlu_confidence_threshold:
                pid = self._queue_pending("PlayPauseMedia", {})
                self.emit(self._json_event("pending", {"id": pid, "intent": "PlayPauseMedia"}))
                return "needs_confirmation"
            ok = await self.prop.play_pause_media()
            self.emit(f"Action: PlayPauseMedia ({'ok' if ok else 'fail'})")
            return "ok" if ok else "fail"

        self.emit(f"Unhandled intent: {intent.name}")
        return "unhandled"

    def _queue_pending(self, name: str, params: dict) -> str:
        pid = str(uuid.uuid4())
        self._pending[pid] = Intent(name=name, params=params, confidence=1.0)
        return pid

    async def confirm_pending(self, pid: str, db: sqlite3.Connection) -> str:
        intent = self._pending.pop(pid, None)
        if not intent:
            self.emit(self._json_event("info", {"msg": f"No pending id {pid}"}))
            return "not_found"
        # Execute with forced high confidence
        intent.confidence = 1.0
        result = await self.handle_intent(intent, db)
        return result

    def cancel_pending(self, pid: str) -> None:
        if pid in self._pending:
            self._pending.pop(pid, None)
            self.emit(self._json_event("info", {"msg": f"Canceled pending {pid}"}))

    @staticmethod
    def _json_event(kind: str, data: dict) -> str:
        import json

        payload = {"type": kind, **data}
        return json.dumps(payload)

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.emit(self._json_event("info", {"msg": f"AI {'enabled' if self._enabled else 'disabled'}"}))
