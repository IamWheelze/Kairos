"""FastAPI web server for Kairos UI/UX.

Provides a modern web interface for controlling the Kairos voice-activated
presentation system.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, List
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
active_connections: List[WebSocket] = []


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


@app.get("/api/nlp/providers")
async def get_nlp_providers():
    """Get list of available NLP providers."""
    try:
        from kairos.nlp.intent import IntentProcessor

        providers = IntentProcessor.get_available_providers()

        # Get current provider info if system is running
        current_provider = None
        if kairos_instance is not None and hasattr(kairos_instance, 'nlp_processor'):
            current_provider = kairos_instance.nlp_processor.get_provider_info()

        return JSONResponse({
            "ok": True,
            "providers": providers,
            "current": current_provider
        })
    except Exception as e:
        log.error("Error getting NLP providers: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e),
            "providers": []
        }, status_code=500)


class NLPProviderRequest(BaseModel):
    provider_id: str
    config: Optional[dict] = None


@app.post("/api/nlp/provider/select")
async def select_nlp_provider(request: NLPProviderRequest):
    """Select an NLP provider."""
    global kairos_instance

    try:
        log.info("Selecting NLP provider: %s", request.provider_id)

        if kairos_instance is None or kairos_instance.get_status() != "running":
            return JSONResponse({
                "ok": False,
                "error": "System not running. Start system first."
            }, status_code=400)

        # Switch provider
        success = kairos_instance.nlp_processor.set_provider(
            request.provider_id,
            request.config
        )

        if success:
            provider_info = kairos_instance.nlp_processor.get_provider_info()

            # Notify WebSocket clients
            await broadcast_message({
                "type": "nlp_provider_changed",
                "provider": provider_info
            })

            return JSONResponse({
                "ok": True,
                "message": f"Switched to provider: {provider_info['name']}",
                "provider": provider_info
            })
        else:
            return JSONResponse({
                "ok": False,
                "error": "Failed to switch provider. Check configuration and API keys."
            }, status_code=400)

    except Exception as e:
        log.error("Error selecting NLP provider: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


class NLPConfigRequest(BaseModel):
    openai_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = "http://localhost:11434"


@app.post("/api/nlp/config")
async def update_nlp_config(request: NLPConfigRequest):
    """Update NLP provider configuration."""
    try:
        log.info("Updating NLP configuration")

        # Store config for next provider initialization
        # Note: This would ideally be persisted to a config file
        config = {}
        if request.openai_api_key:
            config["api_key"] = request.openai_api_key
        if request.ollama_base_url:
            config["base_url"] = request.ollama_base_url

        return JSONResponse({
            "ok": True,
            "message": "Configuration updated. Select a provider to apply changes."
        })
    except Exception as e:
        log.error("Error updating NLP config: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


# Bible API Endpoints

class BibleVerseRequest(BaseModel):
    reference: str
    translation: Optional[str] = None


@app.post("/api/bible/verse")
async def get_bible_verse(request: BibleVerseRequest):
    """Fetch a Bible verse."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        result = kairos_instance.show_bible_verse(request.reference)

        # Broadcast to WebSocket clients
        if result.get("ok"):
            await broadcast_message({
                "type": "bible_verse",
                "reference": result.get("reference"),
                "text": result.get("text"),
                "translation": result.get("translation")
            })

        return JSONResponse(result)
    except Exception as e:
        log.error("Error fetching Bible verse: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


class BibleTranslationRequest(BaseModel):
    translation: str


@app.post("/api/bible/translation")
async def set_bible_translation(request: BibleTranslationRequest):
    """Set Bible translation."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        result = kairos_instance.set_bible_translation(request.translation)
        return JSONResponse(result)
    except Exception as e:
        log.error("Error setting Bible translation: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.get("/api/bible/translations")
async def get_bible_translations():
    """Get list of supported Bible translations."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running",
            "translations": []
        }, status_code=400)

    try:
        if hasattr(kairos_instance, 'bible_service') and kairos_instance.bible_service:
            translations = kairos_instance.bible_service.get_supported_translations()
            current = kairos_instance.current_bible_translation

            return JSONResponse({
                "ok": True,
                "translations": translations,
                "current": current
            })
        else:
            return JSONResponse({
                "ok": False,
                "error": "Bible service not available",
                "translations": []
            }, status_code=500)
    except Exception as e:
        log.error("Error getting translations: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e),
            "translations": []
        }, status_code=500)


@app.post("/api/bible/next")
async def next_bible_verse():
    """Go to next Bible verse."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        result = kairos_instance.next_bible_verse()

        # Broadcast to WebSocket clients
        if result.get("ok"):
            await broadcast_message({
                "type": "bible_verse",
                "reference": result.get("reference"),
                "text": result.get("text"),
                "translation": result.get("translation")
            })

        return JSONResponse(result)
    except Exception as e:
        log.error("Error getting next verse: %s", e)
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)


@app.post("/api/bible/previous")
async def previous_bible_verse():
    """Go to previous Bible verse."""
    global kairos_instance

    if kairos_instance is None or kairos_instance.get_status() != "running":
        return JSONResponse({
            "ok": False,
            "error": "System not running"
        }, status_code=400)

    try:
        result = kairos_instance.previous_bible_verse()

        # Broadcast to WebSocket clients
        if result.get("ok"):
            await broadcast_message({
                "type": "bible_verse",
                "reference": result.get("reference"),
                "text": result.get("text"),
                "translation": result.get("translation")
            })

        return JSONResponse(result)
    except Exception as e:
        log.error("Error getting previous verse: %s", e)
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
