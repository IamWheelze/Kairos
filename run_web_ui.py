#!/usr/bin/env python
"""Launch the Kairos Web UI.

This script starts the FastAPI web server that provides a modern browser-based
interface for controlling the Kairos voice-activated presentation system.
"""

import argparse
from kairos.web.server import run_server


def main():
    parser = argparse.ArgumentParser(
        description="Kairos Voice-Activated Presentation Control - Web UI"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Kairos Voice-Activated Presentation Control - Web UI")
    print("=" * 60)
    print(f"\nStarting web server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"\nOpen your browser and navigate to:")
    print(f"  http://localhost:{args.port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()

    run_server(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
