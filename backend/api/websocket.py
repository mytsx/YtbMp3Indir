"""
WebSocket Handlers for Real-time Progress Updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

websocket_router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for download progress updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, download_id: str, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        if download_id not in self.active_connections:
            self.active_connections[download_id] = []
        self.active_connections[download_id].append(websocket)
        logger.info(f"WebSocket connected for download: {download_id}")

    def disconnect(self, download_id: str, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if download_id in self.active_connections:
            self.active_connections[download_id].remove(websocket)
            if not self.active_connections[download_id]:
                del self.active_connections[download_id]
            logger.info(f"WebSocket disconnected for download: {download_id}")

    async def broadcast(self, download_id: str, message: dict):
        """
        Broadcast a message to all connections for a specific download

        Message format:
        {
            "type": "progress",  // progress, status, error, completed
            "progress": 50,      // 0-100
            "speed": "1.5 MB/s",
            "eta": "00:30"
        }
        """
        if download_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[download_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected.append(connection)

            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(download_id, conn)


# Global connection manager instance
manager = ConnectionManager()


@websocket_router.websocket("/ws/download/{download_id}")
async def websocket_endpoint(websocket: WebSocket, download_id: str):
    """
    WebSocket endpoint for real-time download progress

    Connect: ws://127.0.0.1:<port>/ws/download/{download_id}

    Messages received:
    {
        "type": "progress",
        "progress": 50,
        "speed": "1.5 MB/s",
        "eta": "00:30"
    }
    """
    await manager.connect(download_id, websocket)
    try:
        # Send current download state when connecting
        from services.download_service import get_download_service
        service = get_download_service()
        download = service.get_download(download_id)
        if download:
            # Send current state to newly connected client
            await websocket.send_json({
                "type": "status",
                "status": download.status,
                "progress": download.progress,
                "speed": download.speed,
                "eta": download.eta,
                "video_title": download.video_title,
            })
            logger.info(f"Sent current state to WebSocket: {download.status}, {download.progress}%")

        while True:
            # Keep connection alive
            # Client can send ping/pong messages
            data = await websocket.receive_text()
            logger.debug(f"Received from client: {data}")

            # Echo back for testing
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(download_id, websocket)
        logger.info(f"Client disconnected from download: {download_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(download_id, websocket)


# Export manager for use in download workers
__all__ = ["websocket_router", "manager"]
