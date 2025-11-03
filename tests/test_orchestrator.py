import sqlite3
import pytest
from backend.kairos_core.orchestrator.pipeline import Orchestrator, Intent
from backend.kairos_core.content.db import init_db, get_conn, add_song


class DummyProp:
    async def next_slide(self):
        return True
    async def previous_slide(self):
        return True
    async def clear_screen(self):
        return True
    async def goto_song(self, identifier: str):
        return identifier is not None


@pytest.mark.asyncio
async def test_orchestrator_flow(tmp_path, monkeypatch):
    events = []
    def sink(msg: str):
        events.append(msg)
    orch = Orchestrator(sink, DummyProp())
    # DB
    monkeypatch.setattr('backend.kairos_core.content.db.DB_PATH', str(tmp_path / 'kairos.db'))
    init_db()
    conn = get_conn()
    add_song(conn, 'Amazing Grace', 'Library/Songs/AmazingGrace')
    # High confidence executes
    r = await orch.handle_intent(Intent(name='NextSlide', confidence=1.0), conn)
    assert r == 'ok'
    # Low confidence queues pending
    r2 = await orch.handle_intent(Intent(name='ClearScreen', confidence=0.1), conn)
    assert r2 == 'needs_confirmation'
    # Disabled ignores
    orch.set_enabled(False)
    r3 = await orch.handle_intent(Intent(name='PreviousSlide', confidence=1.0), conn)
    assert r3 == 'disabled'

