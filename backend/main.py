"""
FastAPI Backend Entry Point
Starts server with dynamic port and writes to .backend_port file for Flutter discovery
"""
import sys
import os
import socket
import logging
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import downloads, history, queue, config, conversions
from api.websocket import websocket_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Initialize FastAPI app
app = FastAPI(
    title="MP3Yap Backend",
    version="3.0.0",
    description="YouTube MP3 Downloader Backend API"
)

# CORS middleware (localhost only for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:*", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(conversions.router, prefix="/api/conversions", tags=["conversions"])
app.include_router(websocket_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    from api.websocket import manager
    from services.download_service import get_download_service
    from services.conversion_service import get_conversion_service

    # Inject WebSocket manager into services
    download_service = get_download_service()
    download_service.set_websocket_manager(manager)

    conversion_service = get_conversion_service()
    conversion_service.set_websocket_manager(manager)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "3.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MP3Yap Backend",
        "version": "3.0.0",
        "endpoints": {
            "health": "/api/health",
            "downloads": "/api/downloads",
            "history": "/api/history",
            "queue": "/api/queue",
            "config": "/api/config",
            "websocket": "/ws/download/{download_id}"
        }
    }


def find_free_port(start_port=8000, max_attempts=10):
    """
    Find an available port starting from start_port (TTS pattern)
    More robust than OS-random port selection
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts - 1}")


def write_port_file(port):
    """
    Write the selected port to .backend_port file so Flutter can read it (TTS pattern)
    This is more reliable than parsing stdout
    """
    # Write to project root (one level up from backend/)
    port_file = BASE_DIR.parent / ".backend_port"

    with open(port_file, 'w') as f:
        f.write(str(port))

    logger.info(f"Port {port} written to {port_file}")


def main():
    """
    Start server with dynamic port using TTS-proven pattern
    """
    # Find free port (TTS pattern - more robust)
    try:
        port = find_free_port(8000, 10)
        logger.info(f"Found free port: {port}")
    except RuntimeError as e:
        logger.error(f"Failed to find free port: {e}")
        sys.exit(1)

    # Write port to file for Flutter discovery (TTS pattern)
    write_port_file(port)

    # Also print to stdout for backward compatibility
    print(f"BACKEND_READY PORT={port}", flush=True)
    sys.stdout.flush()

    logger.info(f"Starting MP3Yap Backend on port {port}")

    # Start uvicorn server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        access_log=False  # Reduce noise in stdout
    )


if __name__ == "__main__":
    main()
