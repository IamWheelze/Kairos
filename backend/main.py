from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Callable, Optional
import asyncio
import os

from kairos_core.orchestrator.pipeline import Orchestrator, Intent
from kairos_core.content.db import get_db, init_db
from kairos_core.propresenter.client import ProPresenterClient
from kairos_core.nlu.factory import get_nlu_client
from kairos_core.music_id.acrcloud import ACRCloudClient
from kairos_core.stt.google_speech import GoogleSpeech


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: str) -> None:
        dead: List[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


# Load .env if present (non-fatal)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join("backend", ".env"))
except Exception:
    pass

app = FastAPI(title="Kairos Backend")
templates = Jinja2Templates(directory="backend/templates")
manager = ConnectionManager()


def make_event_sink() -> Callable[[str], None]:
    loop = asyncio.get_event_loop()

    def _sink(msg: str) -> None:
        loop.create_task(manager.broadcast(msg))

    return _sink


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    # Background heartbeat to push ProPresenter status to HITL
    async def heartbeat():
        import json
        while True:
            try:
                status = prop_client.status()
                await manager.broadcast(json.dumps({"type": "pp_status", **status}))
            except Exception:
                pass
            await asyncio.sleep(2)

    asyncio.create_task(heartbeat())


# Mount static directory (optional for simple JS)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")


# Orchestrator single instance with stubbed ProPresenter client
prop_client = ProPresenterClient()
orchestrator = Orchestrator(event_sink=make_event_sink(), propresenter=prop_client)
nlu_client = get_nlu_client()
try:
    acr_client = ACRCloudClient()
except Exception:
    acr_client = None
try:
    stt_client = GoogleSpeech()
except Exception:
    stt_client = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/hitl", response_class=HTMLResponse)
async def hitl(request: Request):
    return templates.TemplateResponse("hitl.html", {"request": request})


@app.websocket("/ws/hitl")
async def ws_hitl(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            # Expect JSON messages for confirm/cancel
            try:
                import json

                data = json.loads(msg)
                if isinstance(data, dict):
                    typ = data.get("type")
                    if typ == "confirm" and data.get("id"):
                        await orchestrator.confirm_pending(data["id"], next(get_db()))
                    elif typ == "cancel" and data.get("id"):
                        orchestrator.cancel_pending(data["id"])
            except Exception:
                # ignore malformed inputs
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/api/intent")
async def api_intent(intent: Intent, db=Depends(get_db)):
    result = await orchestrator.handle_intent(intent, db)
    return {"status": result}


@app.get("/api/propresenter/status")
async def api_prop_status():
    return prop_client.status()


@app.post("/api/nlu/detect")
async def api_nlu_detect(payload: dict, db=Depends(get_db)):
    text = (payload or {}).get("text", "")
    nlu = await nlu_client.detect_intent(text)
    # Map NLUResult to Intent
    intent = Intent(name=nlu.intent if nlu.intent != "Fallback" else "ClearScreen",  # default not used when fallback
                    params=nlu.params, confidence=nlu.confidence or 0.0)
    # If fallback, do not execute; just return
    executed = None
    if nlu.intent != "Fallback":
        executed = await orchestrator.handle_intent(intent, db)
    return {
        "nlu": {
            "intent": nlu.intent,
            "params": nlu.params,
            "confidence": nlu.confidence,
        },
        "executed": executed,
    }


@app.get("/api/nlu/provider")
def api_nlu_provider():
    # Expose which provider is active
    cls = nlu_client.__class__.__name__
    return {"provider": cls}


@app.post("/api/music/identify")
async def api_music_identify(payload: dict, db=Depends(get_db)):
    """Identify song via ACRCloud when audio is provided; otherwise simulate with title.

    Payload options:
    - {"audio_base64": "..."} (preferred)
    - {"title": "..", "confidence": 0.9} (simulation)
    """
    audio_b64 = (payload or {}).get("audio_base64")
    if audio_b64 and acr_client:
        import base64

        try:
            audio_bytes = base64.b64decode(audio_b64)
        except Exception:
            return {"status": "error", "message": "invalid base64"}
        res = await acr_client.identify(audio_bytes)
        if not res.title:
            return {"status": "unrecognized"}
        intent = Intent(name="GoToSong", params={"song_title": res.title}, confidence=res.confidence)
        exec_res = await orchestrator.handle_intent(intent, db)
        return {"status": exec_res, "title": res.title, "artist": res.artist, "confidence": res.confidence}

    # Fallback: title simulation
    title = (payload or {}).get("title")
    confidence = float((payload or {}).get("confidence", 0))
    if not title:
        return {"status": "error", "message": "audio_base64 or title required"}
    intent = Intent(name="GoToSong", params={"song_title": title}, confidence=confidence)
    result = await orchestrator.handle_intent(intent, db)
    return {"status": result}


@app.post("/api/stt/recognize")
async def api_stt_recognize(payload: dict, db=Depends(get_db)):
    if not stt_client:
        return {"status": "error", "message": "STT not configured"}
    b64 = (payload or {}).get("audio_base64")
    mime = (payload or {}).get("mime") or "audio/webm"
    if not b64:
        return {"status": "error", "message": "audio_base64 required"}
    import base64

    try:
        audio_bytes = base64.b64decode(b64)
    except Exception:
        return {"status": "error", "message": "invalid base64"}
    text = await stt_client.recognize_bytes(audio_bytes, mime)
    nlu = await nlu_client.detect_intent(text)
    executed = None
    if nlu.intent != "Fallback":
        executed = await orchestrator.handle_intent(Intent(name=nlu.intent, params=nlu.params, confidence=nlu.confidence or 1.0), db)
    return {"text": text, "nlu": {"intent": nlu.intent, "params": nlu.params, "confidence": nlu.confidence}, "executed": executed}


# Data portal routers
from portal.router import router as portal_router  # noqa

app.include_router(portal_router, prefix="/portal", tags=["portal"])


@app.get("/healthz")
def healthz():
    return {
        "ok": True,
        "propresenter": prop_client.status(),
        "nlu_provider": nlu_client.__class__.__name__,
        "acrcloud": bool(acr_client),
        "stt": bool(stt_client),
    }


@app.get("/readyz")
def readyz():
    st = prop_client.status()
    return {"ready": st.get("connected", False)}


@app.get("/api/state")
def get_state():
    return {"enabled": orchestrator.is_enabled()}


@app.post("/api/state")
async def set_state(payload: dict):
    enabled = bool((payload or {}).get("enabled", True))
    orchestrator.set_enabled(enabled)
    return {"enabled": orchestrator.is_enabled()}
