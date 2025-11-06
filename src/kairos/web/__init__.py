"""Kairos Web UI module.

Provides a modern web interface for controlling the Kairos voice-activated
presentation system using FastAPI and WebSockets.
"""

from .server import app, run_server

__all__ = ["app", "run_server"]
