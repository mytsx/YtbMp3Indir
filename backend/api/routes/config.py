"""
Config API Routes
Handles application configuration management
"""
from fastapi import APIRouter
from ..models import ApiResponse, ErrorDetail, ConfigUpdate
from services.download_service import get_download_service
from services.conversion_service import get_conversion_service
from database.manager import get_database_manager
from config_manager import get_config_manager

router = APIRouter()


@router.get("", response_model=ApiResponse)
async def get_config():
    """
    Get current application configuration

    Response:
    {
        "success": true,
        "data": {
            "output_dir": "/Users/yerli/Music",
            "quality": "320",
            "auto_open": true,
            "language": "tr",
            "history_retention_days": 0
        },
        "error": null
    }
    """
    try:
        config_manager = get_config_manager()
        return ApiResponse(
            success=True,
            data=config_manager.get_all()
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
        config_manager = get_config_manager()

        # Get current values for comparison (before any changes)
        current_retention = config_manager.get('history_retention_days', 0)
        current_output_dir = config_manager.get('output_dir')

        # Update fields that are provided
        update_data = updates.dict(exclude_unset=True)

        # PERSIST FIRST - Save to config file (raises IOError on failure)
        # This ensures no side effects occur if persist fails
        config_manager.update(update_data)

        # THEN APPLY SIDE EFFECTS (only after successful persist)

        # Update services with new output_dir if changed
        if 'output_dir' in update_data and update_data['output_dir'] != current_output_dir:
            download_service = get_download_service()
            conversion_service = get_conversion_service()
            download_service.set_output_dir(update_data['output_dir'])
            conversion_service.set_output_dir(update_data['output_dir'])

        # Cleanup old history if retention days changed to a new value
        if 'history_retention_days' in update_data:
            new_retention = update_data['history_retention_days']
            if new_retention != current_retention and new_retention > 0:
                db_manager = get_database_manager()
                await db_manager.cleanup_old_history(new_retention)

        return ApiResponse(
            success=True,
            data=config_manager.get_all()
        )
    except IOError as e:
        # Config file write failed - settings not persisted
        return ApiResponse(
            success=False,
            error=ErrorDetail(
                code="CONFIG_WRITE_FAILED",
                message=f"Failed to save configuration: {str(e)}"
            )
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="UPDATE_FAILED", message=str(e))
        )
