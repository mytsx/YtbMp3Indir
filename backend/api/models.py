"""
Pydantic Models for API Requests and Responses
"""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


# ============================================================================
# Response Envelope
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str
    message: str


class ApiResponse(BaseModel):
    """
    Standardized API response envelope
    All endpoints should return this format
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None


# ============================================================================
# Download Models
# ============================================================================

class DownloadRequest(BaseModel):
    """Request model for starting a download"""
    url: str = Field(..., description="YouTube video URL")
    quality: str = Field(default="320", description="Audio quality in kbps")


class Download(BaseModel):
    """Download model"""
    id: str
    url: str
    status: str  # downloading, completed, failed, cancelled
    progress: int = 0  # 0-100
    video_title: Optional[str] = None
    error: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime


# ============================================================================
# History Models
# ============================================================================

class HistoryItem(BaseModel):
    """History item model"""
    id: int
    video_title: str
    file_name: str
    file_path: str
    url: str
    downloaded_at: datetime
    file_size: Optional[int] = None
    duration: Optional[int] = None  # seconds
    format: str = "mp3"
    channel_name: Optional[str] = None


# ============================================================================
# Queue Models
# ============================================================================

class QueueItem(BaseModel):
    """Queue item model"""
    id: int
    url: str
    video_title: Optional[str] = None
    priority: int = 0
    position: int = 0
    status: str  # pending, processing, completed, failed
    added_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class QueueItemUpdate(BaseModel):
    """Update queue item"""
    priority: Optional[int] = None
    position: Optional[int] = None


# ============================================================================
# Config Models
# ============================================================================

class AppConfig(BaseModel):
    """Application configuration"""
    output_dir: str
    quality: str = "320"
    auto_open: bool = True
    language: str = "tr"
    history_retention_days: int = 0  # 0 means forever, otherwise delete after N days


class ConfigUpdate(BaseModel):
    """Config update model"""
    output_dir: Optional[str] = None
    quality: Optional[str] = None
    auto_open: Optional[bool] = None
    language: Optional[str] = None
    history_retention_days: Optional[int] = None


# ============================================================================
# WebSocket Models
# ============================================================================

class ProgressUpdate(BaseModel):
    """WebSocket progress update"""
    type: str  # progress, status, error, completed
    download_id: str
    progress: Optional[int] = None
    speed: Optional[str] = None
    eta: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
