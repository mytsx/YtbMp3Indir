"""
FastAPI Backend Entry Point
Starts server with random port and prints to stdout for Flutter discovery
"""
import sys
import socket
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import downloads, history, queue, config
from api.websocket import websocket_router

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
app.include_router(websocket_router)


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


def main():
    """
    Start server with random port and print to stdout
    Flutter will read stdout to discover the port
    """
    # Let OS choose an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]

    # Print port to stdout for Flutter to read
    # IMPORTANT: This line must be exactly in this format
    print(f"BACKEND_READY PORT={port}", flush=True)
    sys.stdout.flush()

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
