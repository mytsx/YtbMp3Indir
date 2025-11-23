"""
Config API Routes
Handles application configuration management
"""
from fastapi import APIRouter
from ..models import ApiResponse, ErrorDetail, AppConfig, ConfigUpdate

router = APIRouter()

# Default configuration
current_config = AppConfig(
    output_dir="/Users/yerli/Music",
    quality="192",
    auto_open=True,
    language="tr"
)


@router.get("", response_model=ApiResponse)
async def get_config():
    """
    Get current application configuration

    Response:
    {
        "success": true,
        "data": {
            "output_dir": "/Users/yerli/Music",
            "quality": "192",
            "auto_open": true,
            "language": "tr"
        },
        "error": null
    }
    """
    try:
        return ApiResponse(
            success=True,
            data=current_config.dict()
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="FETCH_FAILED", message=str(e))
        )


@router.patch("", response_model=ApiResponse)
async def update_config(updates: ConfigUpdate):
    """
    Update application configuration

    Request:
    {
        "output_dir": "/path/to/music",
        "quality": "320",
        "auto_open": false,
        "language": "en"
    }

    Response:
    {
        "success": true,
        "data": {
            "output_dir": "/path/to/music",
            "quality": "320",
            "auto_open": false,
            "language": "en"
        },
        "error": null
    }
    """
    try:
        global current_config

        # Update fields that are provided
        update_data = updates.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(current_config, key, value)

        # TODO: Save to config.json file

        return ApiResponse(
            success=True,
            data=current_config.dict()
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="UPDATE_FAILED", message=str(e))
        )
