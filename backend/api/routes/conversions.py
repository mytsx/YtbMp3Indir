"""
Conversions API Routes
Handles local file conversion to MP3
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Literal
import os
import re
import tempfile
import shutil
from ..models import ApiResponse, ErrorDetail
from services.conversion_service import get_conversion_service
from pydantic import BaseModel, validator

router = APIRouter()

# Get global conversion service
conversion_service = get_conversion_service()

# Allowed quality values
ALLOWED_QUALITIES = {"128", "192", "256", "320"}

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    # Video
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v',
    # Audio
    'wav', 'flac', 'aac', 'm4a', 'ogg', 'wma', 'aiff'
}


def is_valid_media_file(path: str) -> bool:
    """Check if file has allowed extension"""
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    return ext in ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    # Keep only safe characters
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)


class ConversionRequest(BaseModel):
    """Request model for starting a conversion"""
    file_path: str
    quality: str = "320"

    @validator('quality')
    def validate_quality(cls, v):
        if v not in ALLOWED_QUALITIES:
            raise ValueError(f'Quality must be one of: {", ".join(ALLOWED_QUALITIES)}')
        return v


@router.post("", response_model=ApiResponse)
async def create_conversion(request: ConversionRequest):
    """
    Start a new conversion from local file path

    Request:
    {
        "file_path": "/path/to/video.mp4",
        "quality": "320"
    }
    """
    try:
        # Validate file extension
        if not is_valid_media_file(request.file_path):
            return ApiResponse(
                success=False,
                error=ErrorDetail(
                    code="INVALID_FILE_TYPE",
                    message=f"File type not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                )
            )

        conversion = await conversion_service.start_conversion(
            request.file_path,
            request.quality
        )
        return ApiResponse(success=True, data=conversion.to_dict())
    except FileNotFoundError as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FILE_NOT_FOUND", message=str(e))
        )
    except ValueError as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="VALIDATION_ERROR", message=str(e))
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="CONVERSION_FAILED", message=str(e))
        )


@router.post("/upload", response_model=ApiResponse)
async def upload_and_convert(
    file: UploadFile = File(...),
    quality: str = Form(default="320")
):
    """
    Upload a file and convert it to MP3

    This endpoint accepts file uploads for conversion.
    """
    try:
        # Validate quality
        if quality not in ALLOWED_QUALITIES:
            return ApiResponse(
                success=False,
                error=ErrorDetail(
                    code="INVALID_QUALITY",
                    message=f"Quality must be one of: {', '.join(ALLOWED_QUALITIES)}"
                )
            )

        # Validate file extension
        if not is_valid_media_file(file.filename):
            return ApiResponse(
                success=False,
                error=ErrorDetail(
                    code="INVALID_FILE_TYPE",
                    message=f"File type not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                )
            )

        # Sanitize filename to prevent directory traversal
        safe_filename = sanitize_filename(file.filename)

        # Save uploaded file to temp location
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, safe_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Start conversion
        conversion = await conversion_service.start_conversion(temp_path, quality)

        # Note: temp file cleanup should happen after conversion completes
        # For now, we leave it to the OS temp cleanup

        return ApiResponse(success=True, data=conversion.to_dict())
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="UPLOAD_FAILED", message=str(e))
        )


@router.get("", response_model=ApiResponse)
async def get_conversions():
    """Get all active conversions"""
    try:
        conversions = conversion_service.get_all_conversions()
        return ApiResponse(
            success=True,
            data=[c.to_dict() for c in conversions]
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.get("/{conversion_id}", response_model=ApiResponse)
async def get_conversion(conversion_id: str):
    """Get specific conversion details"""
    try:
        conversion = conversion_service.get_conversion(conversion_id)
        if not conversion:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Conversion not found")
            )
        return ApiResponse(success=True, data=conversion.to_dict())
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.delete("/{conversion_id}", response_model=ApiResponse)
async def cancel_conversion(conversion_id: str):
    """Cancel an active conversion"""
    try:
        conversion = conversion_service.get_conversion(conversion_id)
        if not conversion:
            return ApiResponse(
                success=False,
                error=ErrorDetail(code="NOT_FOUND", message="Conversion not found")
            )

        await conversion_service.cancel_conversion(conversion_id)
        return ApiResponse(success=True, data=None)
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="CANCEL_FAILED", message=str(e))
        )
