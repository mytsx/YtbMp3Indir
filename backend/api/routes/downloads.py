"""
Downloads API Routes
Handles download creation, management, and cancellation
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import ApiResponse, ErrorDetail, DownloadRequest, Download
from datetime import datetime
import uuid

router = APIRouter()

# In-memory storage for demo (will be replaced with database)
active_downloads = {}


@router.post("", response_model=ApiResponse)
async def create_download(request: DownloadRequest):
    """
    Start a new download

    Request:
    {
        "url": "https://youtube.com/watch?v=...",
        "quality": "192"
    }

    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "url": "...",
            "status": "downloading",
            "progress": 0,
            ...
        },
        "error": null
    }
    """
    try:
        # Generate unique download ID
        download_id = str(uuid.uuid4())

        # Create download object
        download = Download(
            id=download_id,
            url=request.url,
            status="downloading",
            progress=0,
            created_at=datetime.now()
        )

        # Store in active downloads
        active_downloads[download_id] = download

        # TODO: Start actual download in background
        # asyncio.create_task(download_worker(download_id, request.url, request.quality))

        return ApiResponse(
            success=True,
            data=download.dict()
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="DOWNLOAD_FAILED", message=str(e))
        )


@router.get("", response_model=ApiResponse)
async def get_downloads():
    """
    Get all active downloads

    Response:
    {
        "success": true,
        "data": [
            {
                "id": "uuid",
                "url": "...",
                "status": "downloading",
                "progress": 50,
                ...
            }
        ],
        "error": null
    }
    """
    try:
        downloads = list(active_downloads.values())
        return ApiResponse(
            success=True,
            data=[d.dict() for d in downloads]
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.get("/{download_id}", response_model=ApiResponse)
async def get_download(download_id: str):
    """
    Get specific download details

    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "url": "...",
            "status": "downloading",
            "progress": 50,
            ...
        },
        "error": null
    }
    """
    try:
        if download_id not in active_downloads:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Download not found")
            )

        download = active_downloads[download_id]
        return ApiResponse(
            success=True,
            data=download.dict()
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.delete("/{download_id}", response_model=ApiResponse)
async def cancel_download(download_id: str):
    """
    Cancel an active download

    Response:
    {
        "success": true,
        "data": null,
        "error": null
    }
    """
    try:
        if download_id not in active_downloads:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Download not found")
            )

        # TODO: Cancel actual download process
        # Cancel yt-dlp process and clean up files

        # Remove from active downloads
        del active_downloads[download_id]

        return ApiResponse(
            success=True,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="CANCEL_FAILED", message=str(e))
        )
