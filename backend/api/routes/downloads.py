"""
Downloads API Routes
Handles download creation, management, and cancellation
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import ApiResponse, ErrorDetail, DownloadRequest
from services.download_service import get_download_service
from datetime import datetime

router = APIRouter()

# Get global download service
download_service = get_download_service()


@router.post("", response_model=ApiResponse)
async def create_download(request: DownloadRequest):
    """
    Start a new download

    Request:
    {
        "url": "https://youtube.com/watch?v=...",
        "quality": "320"
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
        # Start download using service
        download = await download_service.start_download(request.url, request.quality)

        return ApiResponse(
            success=True,
            data=download.to_dict()
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
        downloads = download_service.get_all_downloads()
        return ApiResponse(
            success=True,
            data=[d.to_dict() for d in downloads]
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
        download = download_service.get_download(download_id)
        if not download:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Download not found")
            )

        return ApiResponse(
            success=True,
            data=download.to_dict()
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
        download = download_service.get_download(download_id)
        if not download:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Download not found")
            )

        # Cancel download
        download_service.cancel_download(download_id)

        return ApiResponse(
            success=True,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="CANCEL_FAILED", message=str(e))
        )
