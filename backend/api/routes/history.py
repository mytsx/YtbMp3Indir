"""
History API Routes
Handles download history retrieval and management
"""
from fastapi import APIRouter, Query
from ..models import ApiResponse, ErrorDetail
from database.manager import get_database_manager
from services.download_service import get_download_service
from datetime import datetime

router = APIRouter()

# Get global managers
db_manager = get_database_manager()
download_service = get_download_service()


@router.get("", response_model=ApiResponse)
async def get_history(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """
    Get download history

    Query params:
    - limit: Max items to return (default 100, max 500)
    - offset: Skip first N items (default 0)

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
        history = await db_manager.get_history(limit=limit, offset=offset)
        return ApiResponse(
            success=True,
            data=history
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.get("/search", response_model=ApiResponse)
async def search_history(q: str = Query(..., min_length=1)):
    """
    Search download history by video title

    Query params:
    - q: Search query (required, min 1 character)

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "video_title": "Matching Song Name",
                ...
            }
        ],
        "error": null
    }
    """
    try:
        results = await db_manager.search_history(q)
        return ApiResponse(
            success=True,
            data=results
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="SEARCH_FAILED", message=str(e))
        )


@router.get("/stats", response_model=ApiResponse)
async def get_statistics():
    """
    Get download statistics

    Response:
    {
        "success": true,
        "data": {
            "total_downloads": 42,
            "total_size": 125829120,
            "total_duration": 7200
        },
        "error": null
    }
    """
    try:
        stats = await db_manager.get_statistics()
        return ApiResponse(
            success=True,
            data=stats
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="STATS_FAILED", message=str(e))
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
        item = await db_manager.get_history_item(history_id)

        if not item:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="History item not found")
            )

        return ApiResponse(
            success=True,
            data=item
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
        # Get item from database
        item = await db_manager.get_history_item(history_id)

        if not item:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="History item not found")
            )

        # Start new download using the URL from history
        download = await download_service.start_download(item['url'])

        return ApiResponse(
            success=True,
            data=download.to_dict()
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
        # Soft delete in database
        deleted = await db_manager.delete_history_item(history_id)

        if not deleted:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="History item not found")
            )

        return ApiResponse(
            success=True,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="DELETE_FAILED", message=str(e))
        )
