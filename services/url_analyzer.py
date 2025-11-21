"""
URL Analysis Service
Handles URL validation, playlist detection, and database checks in background
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import yt_dlp

from utils.translation_manager import translation_manager

logger = logging.getLogger(__name__)


class UrlAnalysisResult:
    """Container for URL analysis results"""
    def __init__(self):
        self.valid_urls: List[str] = []
        self.invalid_urls: List[str] = []
        self.playlist_info: List[Dict[str, Any]] = []
        self.already_downloaded: int = 0
        self.files_exist: int = 0
        self.files_missing: int = 0
        self.total_videos: int = 0


class UrlAnalyzer:
    """Pure function URL analysis logic"""
    
    # YouTube URL regex patterns
    # Pattern for video URLs (watch, shorts, embed, youtu.be)
    VIDEO_REGEX = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})'
    )

    # Pattern for playlist URLs (can be playlist-only or with video)
    PLAYLIST_REGEX = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/(playlist\?list=|watch\?.*[&?]list=))([a-zA-Z0-9_-]+)'
    )

    # YouTube playlist ID patterns (for stricter validation)
    # Common prefixes: PL (playlist), UU (user uploads), OLAK (album), RDCLAK (radio), WL (watch later), LL (liked)
    PLAYLIST_ID_PATTERN = re.compile(
        r'^(PL|UU|OLAK|RDCLAK|WL|LL|RD)[a-zA-Z0-9_-]{10,}$|^[a-zA-Z0-9_-]{13,}$'
    )
    
    @classmethod
    def validate_youtube_urls(cls, urls: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate YouTube URLs using regex (supports both video and playlist URLs)

        Returns:
            Tuple of (valid_urls, invalid_urls)
        """
        valid_urls = []
        invalid_urls = []

        for url in urls:
            url = url.strip()
            if not url:
                continue

            # Check for video URL first
            video_match = cls.VIDEO_REGEX.search(url)
            if video_match:
                video_id = video_match.group(5)
                # Validate video ID: must be 11 characters, alphanumeric + _ and -
                if video_id and len(video_id) == 11 and video_id.replace('-', '').replace('_', '').isalnum():
                    valid_urls.append(url)
                    continue

            # Check for playlist URL
            playlist_match = cls.PLAYLIST_REGEX.search(url)
            if playlist_match:
                playlist_id = playlist_match.group(5)
                # IMPROVED: Validate with YouTube-specific playlist ID patterns
                # This prevents false positives from non-YouTube URLs with list= parameter
                if playlist_id and cls.PLAYLIST_ID_PATTERN.match(playlist_id):
                    valid_urls.append(url)
                    continue
                elif playlist_id and len(playlist_id) >= 10 and playlist_id.replace('-', '').replace('_', '').isalnum():
                    # Fallback: Accept if at least 10 chars and alphanumeric (might be new format)
                    valid_urls.append(url)
                    continue

            # Neither video nor playlist format matched
            invalid_urls.append(url)

        return valid_urls, invalid_urls
    
    @classmethod
    def extract_playlist_info(cls, url: str) -> Dict[str, Any]:
        """
        Extract playlist information from URL using yt-dlp
        
        Returns:
            Dictionary with playlist info or None if failed
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
                'ignoreerrors': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and info.get('_type') == 'playlist':
                    playlist_title = info.get('title', translation_manager.tr("common.labels.unnamed_playlist"))
                    playlist_size = info.get('playlist_count', 0)
                    if playlist_size == 0 and 'entries' in info:
                        playlist_size = len(info['entries'])
                    uploader = info.get('uploader', info.get('channel', ''))
                    
                    return {
                        'url': url,
                        'is_playlist': True,
                        'title': playlist_title,
                        'video_count': playlist_size,
                        'uploader': uploader
                    }
                else:
                    return {
                        'url': url,
                        'is_playlist': False,
                        'title': translation_manager.tr("common.labels.single_video"),
                        'video_count': 1
                    }
        except Exception as e:
            logger.warning(f"Playlist bilgisi alınamadı: {e}")
            return {
                'url': url,
                'is_playlist': False,
                'title': translation_manager.tr("common.labels.unknown"),
                'video_count': 1
            }
    
    @classmethod
    def check_file_existence(cls, file_path: str, file_name: str, output_dir: str) -> bool:
        """
        Check if a downloaded file exists on disk
        
        Args:
            file_path: Path from database
            file_name: Filename from database
            output_dir: Default output directory
            
        Returns:
            True if file exists, False otherwise
        """
        # Try primary path
        if file_path and file_name:
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            full_path = os.path.join(file_path, file_name)
            if os.path.exists(full_path):
                return True
            
            # Try with pipe character replacement
            alt_file_name = file_name.replace('|', '｜')
            alt_path = os.path.join(file_path, alt_file_name)
            if os.path.exists(alt_path):
                return True
        
        # Try output directory
        if file_name and output_dir:
            if not os.path.isabs(output_dir):
                output_dir = os.path.abspath(output_dir)
            
            alt_path = os.path.join(output_dir, file_name)
            if os.path.exists(alt_path):
                return True
            
            # Try with pipe character replacement
            alt_file_name = file_name.replace('|', '｜')
            alt_path2 = os.path.join(output_dir, alt_file_name)
            if os.path.exists(alt_path2):
                return True
        
        return False


class UrlAnalysisWorker(QThread):
    """Background worker for URL analysis"""
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(str)  # Status message
    finished = pyqtSignal(object)  # UrlAnalysisResult
    error = pyqtSignal(str)
    
    def __init__(self, urls: List[str], db_manager, config: Dict[str, Any], 
                 url_cache: Dict[str, Any], parent: Optional[QObject] = None):
        super().__init__(parent)
        self.urls = urls
        self.db_manager = db_manager
        self.config = config
        self.url_cache = url_cache
        self._is_cancelled = False
    
    def cancel(self):
        """Cancel the analysis"""
        self._is_cancelled = True
    
    def run(self):
        """Run URL analysis in background"""
        result = UrlAnalysisResult()

        try:
            self.started.emit()

            # Step 1: Validate URLs
            self.progress.emit("⏳ URL'ler kontrol ediliyor...")
            result.valid_urls, result.invalid_urls = UrlAnalyzer.validate_youtube_urls(self.urls)

            if self._is_cancelled:
                return  # Will emit finished in finally block

            # Step 2: Check for playlists
            has_playlist = any('list=' in url for url in result.valid_urls)
            if has_playlist:
                self.progress.emit("⏳ Playlist bilgisi alınıyor...")

            # Step 3: Extract playlist information
            for url in result.valid_urls:
                if self._is_cancelled:
                    return  # Will emit finished in finally block

                if 'list=' in url:
                    # This is a playlist URL
                    playlist_data = UrlAnalyzer.extract_playlist_info(url)
                    result.playlist_info.append(playlist_data)

                    # Update cache (caller should handle cache size)
                    if url not in self.url_cache:
                        self.url_cache[url] = {
                            'is_playlist': playlist_data.get('is_playlist', False),
                            'title': playlist_data.get('title', translation_manager.tr("common.labels.unknown")),
                            'video_count': playlist_data.get('video_count', 1),
                            'uploader': playlist_data.get('uploader', '')
                        }
                else:
                    # Single video
                    result.playlist_info.append({
                        'url': url,
                        'title': translation_manager.tr("common.labels.single_video"),
                        'video_count': 1
                    })
                    if url not in self.url_cache:
                        self.url_cache[url] = {
                            'is_playlist': False,
                            'title': translation_manager.tr("common.labels.single_video"),
                            'video_count': 1
                        }

            if self._is_cancelled:
                return  # Will emit finished in finally block

            # Step 4: Check database for existing downloads
            self.progress.emit("⏳ Veritabanı kontrol ediliyor...")
            output_dir = self.config.get('output_path', 'music')

            for url in result.valid_urls:
                if self._is_cancelled:
                    return  # Will emit finished in finally block

                existing = self.db_manager.get_download_by_url(url)
                if existing:
                    result.already_downloaded += 1
                    latest_record = existing[0]  # Most recent record

                    # Check file existence
                    file_exists = UrlAnalyzer.check_file_existence(
                        latest_record.get('file_path'),
                        latest_record.get('file_name'),
                        output_dir
                    )

                    if file_exists:
                        result.files_exist += 1
                    else:
                        result.files_missing += 1

            # Calculate total videos
            result.total_videos = sum(p.get('video_count', 1)
                                     for p in result.playlist_info)

        except Exception as e:
            self.error.emit(str(e))

        finally:
            # FIX P0-5: ALWAYS emit finished signal, even on cancellation or error
            # This prevents UI from hanging when analysis is cancelled
            self.finished.emit(result)