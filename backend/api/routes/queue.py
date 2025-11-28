"""
Queue API Routes
Handles download queue management with priority and position
"""
from fastapi import APIRouter, Query
from ..models import ApiResponse, ErrorDetail
from database.manager import get_database_manager

router = APIRouter()

# Get global database manager
db_manager = get_database_manager()


@router.get("", response_model=ApiResponse)
async def get_queue(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """
    Get download queue items

    Query params:
    - limit: Max items to return (default 100, max 500)
    - offset: Skip first N items (default 0)

    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "url": "https://youtube.com/...",
                "video_title": "Song Name",
                "priority": 0,
                "position": 0,
                "status": "pending",
                "added_at": "2025-11-23T10:00:00"
            }
        ],
        "error": null
    }
    """
    try:
        queue = await db_manager.get_queue(limit=limit, offset=offset)
        return ApiResponse(
            success=True,
            data=queue
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.post("", response_model=ApiResponse)
async def add_to_queue(url: str, priority: int = 0):
    """
    Add item to download queue

    Request:
    {
        "url": "https://youtube.com/...",
        "priority": 0
    }

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "url": "...",
            "priority": 0,
            "status": "pending"
        },
        "error": null
    }
    """
    try:
        queue_id = await db_manager.add_to_queue(url, priority)
        item = await db_manager.get_queue_item(queue_id)

        return ApiResponse(
            success=True,
            data=item
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="ADD_FAILED", message=str(e))
        )


@router.patch("/{queue_id}/priority", response_model=ApiResponse)
async def update_priority(queue_id: int, priority: int):
    """
    Update queue item priority

    Request:
    {
        "priority": 5
    }

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "priority": 5,
            ...
        },
        "error": null
    }
    """
    try:
        success = await db_manager.update_queue_priority(queue_id, priority)

        if not success:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Queue item not found")
            )

        item = await db_manager.get_queue_item(queue_id)
        return ApiResponse(
            success=True,
            data=item
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="UPDATE_FAILED", message=str(e))
        )


@router.patch("/{queue_id}/position", response_model=ApiResponse)
async def update_position(queue_id: int, position: int):
    """
    Update queue item position (reorder)

    Request:
    {
        "position": 2
    }

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "position": 2,
            ...
        },
        "error": null
    }
    """
    try:
        success = await db_manager.update_queue_position(queue_id, position)

        if not success:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Queue item not found")
            )

        item = await db_manager.get_queue_item(queue_id)
        return ApiResponse(
            success=True,
            data=item
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="UPDATE_FAILED", message=str(e))
        )


@router.delete("/{queue_id}", response_model=ApiResponse)
async def delete_queue_item(queue_id: int):
    """
    Remove item from queue (soft delete)

    Response:
    {
        "success": true,
        "data": null,
        "error": null
    }
    """
    try:
        deleted = await db_manager.delete_queue_item(queue_id)

        if not deleted:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Queue item not found")
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


@router.post("/clear", response_model=ApiResponse)
async def clear_queue(status: str = "all"):
    """
    Clear queue items by status

    Query params:
    - status: Filter by status (pending, completed, failed, all)

    Response:
    {
        "success": true,
        "data": {
            "deleted_count": 5
        },
        "error": null
    }
    """
    try:
        count = await db_manager.clear_queue(status)

        return ApiResponse(
            success=True,
            data={"deleted_count": count}
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="CLEAR_FAILED", message=str(e))
        )
