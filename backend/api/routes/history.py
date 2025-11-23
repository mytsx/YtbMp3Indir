"""
History API Routes
Handles download history retrieval and management
"""
from fastapi import APIRouter
from ..models import ApiResponse, ErrorDetail, HistoryItem
from datetime import datetime

router = APIRouter()

# In-memory storage for demo (will be replaced with database)
history_items = []


@router.get("", response_model=ApiResponse)
async def get_history():
    """
    Get download history

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "video_title": "Song Name",
                "file_name": "song.mp3",
                "file_path": "/path/to/music/song.mp3",
                "downloaded_at": "2025-11-23T10:00:00",
                "file_size": 5242880,
                "duration": 180
            }
        ],
        "error": null
    }
    """
    try:
        return ApiResponse(
            success=True,
            data=[item.dict() for item in history_items]
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.get("/{history_id}", response_model=ApiResponse)
async def get_history_item(history_id: int):
    """
    Get specific history item

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "video_title": "Song Name",
            ...
        },
        "error": null
    }
    """
    try:
        # Find item by ID
        item = next((h for h in history_items if h.id == history_id), None)

        if not item:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="History item not found")
            )

        return ApiResponse(
            success=True,
            data=item.dict()
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.post("/{history_id}/redownload", response_model=ApiResponse)
async def redownload(history_id: int):
    """
    Re-download a file from history

    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "url": "...",
            "status": "downloading",
            ...
        },
        "error": null
    }
    """
    try:
        # Find item by ID
        item = next((h for h in history_items if h.id == history_id), None)

        if not item:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="History item not found")
            )

        # TODO: Start download using the URL from history
        # from .downloads import create_download
        # return await create_download(DownloadRequest(url=item.url))

        return ApiResponse(
            success=True,
            data={"message": "Re-download started", "url": item.url}
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="REDOWNLOAD_FAILED", message=str(e))
        )


@router.delete("/{history_id}", response_model=ApiResponse)
async def delete_history_item(history_id: int):
    """
    Soft delete a history item

    Response:
    {
        "success": true,
        "data": null,
        "error": null
    }
    """
    try:
        # Find item by ID
        item = next((h for h in history_items if h.id == history_id), None)

        if not item:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="History item not found")
            )

        # TODO: Mark as deleted in database (soft delete)
        # For now, just remove from list
        history_items.remove(item)

        return ApiResponse(
            success=True,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="DELETE_FAILED", message=str(e))
        )
