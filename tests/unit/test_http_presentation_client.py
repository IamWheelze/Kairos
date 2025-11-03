import json
from types import SimpleNamespace
from kairos.presentation.http_client import HTTPPresentationClient


class _FakeResponse:
    def __init__(self, payload: dict):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_http_client_route_and_payload(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=0):  # noqa: ARG001
        captured["url"] = req.full_url
        body = req.data.decode("utf-8")
        captured["json"] = json.loads(body)
        return _FakeResponse({"ok": True, "echo": captured["json"]})

    # Patch urllib.request.urlopen
    import urllib.request as ureq

    monkeypatch.setattr(ureq, "urlopen", fake_urlopen)

    client = HTTPPresentationClient(
        base_url="http://localhost:1234",
        routes={
            "next_slide": "/api/next",
        },
    )

    result = client.send_command("next_slide", presentation_id="deck-1")
    assert result["ok"] is True
    assert captured["url"].endswith("/api/next")
    assert captured["json"]["command"] == "next_slide"
    assert captured["json"]["presentation_id"] == "deck-1"
