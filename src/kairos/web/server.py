"""FastAPI web server for Kairos UI/UX.

Provides a modern web interface for controlling the Kairos voice-activated
presentation system.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from kairos.core import Kairos
from kairos.logging import get_logger

log = get_logger("kairos.web.server")

# Initialize FastAPI app
app = FastAPI(title="Kairos Voice-Activated Presentation Control")

# Get paths
WEB_DIR = Path(__file__).parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Kairos instance
kairos_instance: Optional[Kairos] = None

# WebSocket connections
active_connections: list[WebSocket] = []


# Request Models
class TextCommandRequest(BaseModel):
    command: str


class RecordingRequest(BaseModel):
    duration: int = 5


class SettingsRequest(BaseModel):
    asrEngine: str = "google"
    language: str = "en-US"
    sampleRate: int = 44100
    apiClient: str = "stub"
    apiUrl: str = ""


# Routes
@app.get("/")
async def index(request: Request):
    """Serve the main UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/system/status")
async def get_system_status():
    """Get current system status."""
    global kairos_instance

    if kairos_instance is None:
        return JSONResponse({
            "status": "stopped",
            "running": False
        })

    status = kairos_instance.get_status()
    return JSONResponse({
        "status": status,
        "running": status == "running"
    })


@app.post("/api/system/start")
async def start_system():
    """Start the Kairos system."""
    global kairos_instance

    try:
        if kairos_instance is None:
            kairos_instance = Kairos()

        kairos_instance.start()
        log.info("System started via web UI")

        # Notify WebSocket clients
        await broadcast_message({
            "type": "status_update",
            "status": "running"
        })

        return JSONResponse({
            "ok": True,
            "status": "running",
            "message": "System started successfully"
        })
    except Exception as e:
        log.error("Failed to start system: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.post("/api/system/stop")
async def stop_system():
    """Stop the Kairos system."""
    global kairos_instance

    try:
        if kairos_instance is not None:
            kairos_instance.stop()
            log.info("System stopped via web UI")

        # Notify WebSocket clients
        await broadcast_message({
            "type": "status_update",
            "status": "stopped"
        })

        return JSONResponse({
            "ok": True,
            "status": "stopped",
            "message": "System stopped successfully"
        })
    except Exception as e:
        log.error("Failed to stop system: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.post("/api/command/text")
async def process_text_command(request: TextCommandRequest):
    """Process a text command."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        log.info("Processing text command: %s", request.command)
        result = kairos_instance.process_command(request.command)

        # Notify WebSocket clients
        await broadcast_message({
            "type": "transcription",
            "text": request.command,
            "intent": result.get("command", "unknown")
        })

        return JSONResponse({
            "ok": result.get("ok", True),
            "command": result.get("command"),
            "result": result
        })
    except Exception as e:
        log.error("Error processing text command: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.post("/api/voice/record")
async def record_voice_command(request: RecordingRequest):
    """Record and process a voice command."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        log.info("Recording voice command for %d seconds", request.duration)

        # Notify recording started
        await broadcast_message({
            "type": "status_update",
            "status": "recording"
        })

        result = kairos_instance.process_voice_command_interactive(duration=request.duration)

        # Notify recording completed
        await broadcast_message({
            "type": "status_update",
            "status": "running"
        })

        if result.get("transcription"):
            await broadcast_message({
                "type": "transcription",
                "text": result["transcription"],
                "intent": result.get("intent", "unknown")
            })

        return JSONResponse(result)
    except Exception as e:
        log.error("Error recording voice command: %s", e)

        # Reset status
        await broadcast_message({
            "type": "status_update",
            "status": "running"
        })

        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.post("/api/voice/process-file")
async def process_audio_file(file: UploadFile = File(...)):
    """Process an uploaded audio file."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    # Save uploaded file to temp location
    temp_file = None
    try:
        # Create temp file with original extension
        suffix = Path(file.filename).suffix if file.filename else ".wav"
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_path = temp_file.name

        # Write uploaded content
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        log.info("Processing audio file: %s", file.filename)

        # Process the audio file
        result = kairos_instance.process_audio_file(temp_path)

        if result.get("transcription"):
            await broadcast_message({
                "type": "transcription",
                "text": result["transcription"],
                "intent": result.get("intent", "unknown")
            })

        return JSONResponse(result)

    except Exception as e:
        log.error("Error processing audio file: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

    finally:
        # Clean up temp file
        if temp_file:
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@app.get("/api/presentation/current-slide")
async def get_current_slide():
    """Get the current slide number."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        result = kairos_instance.presentation_controller.get_current_slide()
        return JSONResponse({
            "ok": result.get("ok", True),
            "slide": result.get("current_slide", "-")
        })
    except Exception as e:
        log.error("Error getting current slide: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.get("/api/presentation/list")
async def get_presentations():
    """Get list of available presentations."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running",
            "presentations": []
        }, status_code=400)

    try:
        result = kairos_instance.presentation_controller.get_presentations()
        presentations = result.get("presentations", [])

        return JSONResponse({
            "ok": result.get("ok", True),
            "presentations": presentations
        })
    except Exception as e:
        log.error("Error getting presentations: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e),
            "presentations": []
        }, status_code=500)


@app.post("/api/settings/update")
async def update_settings(settings: SettingsRequest):
    """Update system settings."""
    global kairos_instance

    try:
        log.info("Updating settings: %s", settings.dict())

        # If system is running, apply settings
        if kairos_instance is not None and kairos_instance.get_status() == "running":
            # Update ASR model settings
            if hasattr(kairos_instance.asr_model, 'model_name'):
                kairos_instance.asr_model.model_name = settings.asrEngine
                kairos_instance.asr_model.language = settings.language

            # Update audio recorder settings
            if hasattr(kairos_instance.audio_recorder, 'rate'):
                kairos_instance.audio_recorder.rate = settings.sampleRate

            # Note: For full settings update, system may need to be restarted

        return JSONResponse({
            "ok": True,
            "message": "Settings updated. Restart system for changes to take full effect."
        })
    except Exception as e:
        log.error("Error updating settings: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    log.info("WebSocket client connected")

    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            log.debug("Received WebSocket message: %s", data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        log.info("WebSocket client disconnected")


async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients."""
    for connection in active_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_json(message)
        except Exception as e:
            log.error("Error sending to WebSocket client: %s", e)
            try:
                active_connections.remove(connection)
            except ValueError:
                pass


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "kairos-web"
    })


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the web server.

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8000)
        reload: Enable auto-reload for development (default: False)
    """
    log.info("Starting Kairos web server on %s:%d", host, port)
    uvicorn.run(
        "kairos.web.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server(reload=True)
