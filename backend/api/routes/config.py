"""
Config API Routes
Handles application configuration management
"""
from fastapi import APIRouter
from ..models import ApiResponse, ErrorDetail, AppConfig, ConfigUpdate
from services.download_service import get_download_service
from services.conversion_service import get_conversion_service
from database.manager import get_database_manager

router = APIRouter()

# Default configuration
current_config = AppConfig(
    output_dir="/Users/yerli/Music",
    quality="192",
    auto_open=True,
    language="tr",
    history_retention_days=0  # 0 = keep forever
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

        # Update services with new output_dir if changed
        if 'output_dir' in update_data:
            download_service = get_download_service()
            conversion_service = get_conversion_service()
            download_service.set_output_dir(update_data['output_dir'])
            conversion_service.set_output_dir(update_data['output_dir'])

        # Cleanup old history if retention days changed
        if 'history_retention_days' in update_data:
            retention_days = update_data['history_retention_days']
            if retention_days > 0:
                db_manager = get_database_manager()
                await db_manager.cleanup_old_history(retention_days)

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
