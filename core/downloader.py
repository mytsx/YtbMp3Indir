import os
import shutil
import threading
import logging
from typing import Optional, Dict, Any, List
import yt_dlp
import static_ffmpeg
from PyQt5.QtCore import QObject, pyqtSignal
from database.manager import DatabaseManager
from utils.translation_manager import translation_manager

logger = logging.getLogger(__name__)


class DownloadSignals(QObject):
    """İndirme işlemleri için sinyal sınıfı"""
    progress = pyqtSignal(str, float, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str)
    status_update = pyqtSignal(str)


class Downloader:
    """YouTube video indirme ve MP3 dönüştürme sınıfı"""

    # Filename truncation safety margin (bytes)
    # Provides buffer for multi-byte UTF-8 characters and formatting overhead
    FILENAME_TRUNCATION_SAFETY_MARGIN = 10

    # Logger interface for yt-dlp
    def debug(self, msg: str) -> None:
        """Called by yt-dlp for debug messages

        Args:
            msg: Debug message from yt-dlp

        Parses playlist download progress and emits status updates.
        """
        # Parse playlist download messages
        if '[download] Downloading item' in msg:
            import re
            match = re.search(r'Downloading item (\d+) of (\d+)', msg)
            if match:
                self.current_item_index = int(match.group(1))
                self.playlist_total = int(match.group(2))
                self.signals.status_update.emit(f"📥 [{self.current_item_index}/{self.playlist_total}] Playlist indiriliyor...")

    def warning(self, msg: str) -> None:
        """Called by yt-dlp for warnings

        Args:
            msg: Warning message from yt-dlp
        """
        pass

    def error(self, msg: str) -> None:
        """Called by yt-dlp for errors

        Args:
            msg: Error message from yt-dlp

        Emits status update signal with error message.
        """
        self.signals.status_update.emit(f"❌ Hata: {msg}")
    
    def __init__(self, signals: DownloadSignals) -> None:
        """Initialize the downloader with download signals

        Args:
            signals: DownloadSignals instance for emitting progress and status updates

        Sets up the download engine including:
        - FFmpeg availability detection and auto-installation
        - Thread-safe data structures for multi-threaded downloads
        - Database connection for download history
        - Playlist tracking mechanisms
        """
        self.signals = signals
        self.is_running = False
        self.current_url = None
        self.db_manager = DatabaseManager()
        self.ydl = None  # Current YoutubeDL instance for cancellation
        self.current_output_path = None  # Store output path for hooks

        # Thread-safe data structures
        self._lock = threading.Lock()
        self._saved_videos = set()
        self._current_temp_files = set()  # Track temp files for cleanup

        # Playlist tracking
        self.playlist_info = {}  # URL -> playlist info
        self.current_playlist_index = {}  # URL -> current index
        self.current_item_index = 0  # Track current item in playlist
        self.playlist_total = 0  # Total items in playlist
        # Static FFmpeg'i yükle ve kullan
        try:
            static_ffmpeg.add_paths()
            self.ffmpeg_available = True
        except (ImportError, OSError, RuntimeError) as e:
            self.ffmpeg_available = self.check_system_ffmpeg()
            if not self.ffmpeg_available:
                self.signals.status_update.emit(translation_manager.tr('downloader.errors.ffmpeg_load_failed').format(error=str(e)))
    
    def check_system_ffmpeg(self) -> bool:
        """Check if FFmpeg is available in system PATH

        Returns:
            True if FFmpeg is found in system PATH, False otherwise
        """
        return shutil.which('ffmpeg') is not None

    def _cleanup_temp_files(self, base_filename: Optional[str] = None) -> None:
        """
        Clean up temporary download files (.part, .ytdl, incomplete files)

        Args:
            base_filename: Specific file to clean up (optional)
                         If None, cleans all tracked temp files
        """
        files_to_clean = set()

        if base_filename:
            # Clean specific file and its variants
            files_to_clean.add(base_filename)
            files_to_clean.add(base_filename + '.part')
            files_to_clean.add(base_filename + '.ytdl')
            # Also check for common yt-dlp temp file patterns
            if not base_filename.endswith(('.part', '.ytdl')):
                dir_path = os.path.dirname(base_filename) or '.'
                base_name = os.path.basename(base_filename)
                try:
                    for file in os.listdir(dir_path):
                        # Match .part and .ytdl files for this download
                        if file.startswith(base_name) and (file.endswith('.part') or file.endswith('.ytdl')):
                            files_to_clean.add(os.path.join(dir_path, file))
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not list directory for cleanup: {e}")
        else:
            # Clean all tracked temp files
            with self._lock:
                files_to_clean.update(self._current_temp_files)

            # Also clean output directory for any orphaned temp files
            if self.current_output_path and os.path.exists(self.current_output_path):
                try:
                    for file in os.listdir(self.current_output_path):
                        if file.endswith('.part') or file.endswith('.ytdl'):
                            files_to_clean.add(os.path.join(self.current_output_path, file))
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not list output directory for cleanup: {e}")

        # Perform cleanup
        cleaned_count = 0
        for file_path in files_to_clean:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.info(f"Cleaned up temp file: {os.path.basename(file_path)}")
                except PermissionError as e:
                    logger.error(f"Permission denied when cleaning {file_path}: {e}")
                except OSError as e:
                    logger.error(f"OS error when cleaning {file_path}: {e}")
                except Exception:
                    logger.exception(f"Unexpected error when cleaning {file_path}")

        # Clear tracked files if doing full cleanup
        if not base_filename:
            with self._lock:
                self._current_temp_files.clear()

        if cleaned_count > 0:
            logger.info(f"Cleanup complete: removed {cleaned_count} temporary file(s)")

    def save_to_database(self, info: Dict[str, Any]) -> None:
        """Save video metadata to database

        Args:
            info: Video information dictionary from yt-dlp containing:
                - id: Video ID
                - title: Video title
                - ext: File extension
                - webpage_url: Full video URL
                - filesize: File size in bytes
                - duration: Video duration in seconds
                - uploader: Channel name

        Thread-safe operation that prevents duplicate database entries
        using video ID tracking. Handles filename sanitization matching
        yt-dlp's template pattern.
        """
        if not info:
            return
        
        # Check if already saved (thread-safe)
        video_id = info.get('id', '')
        with self._lock:
            if video_id in self._saved_videos:
                return
            
        title = info.get('title', 'Unknown')
        ext = info.get('ext', 'webm')

        # CRITICAL FIX: Build file_name matching yt-dlp template pattern
        # Template: '%(title).200B [%(id)s].%(ext)s'
        # We must sanitize and truncate the same way yt-dlp does
        try:
            from yt_dlp.utils import sanitize_filename
            # Sanitize title (removes illegal chars, Windows-compatible)
            sanitized_title = sanitize_filename(title, restricted=False, is_id=False)
            # Truncate to approximately 200 bytes (yt-dlp's .200B)
            # Account for " [video_id]" suffix and extension
            max_title_bytes = 200 - len(f" [{video_id}]") - len(f".{ext if not self.ffmpeg_available else 'mp3'}") - self.FILENAME_TRUNCATION_SAFETY_MARGIN
            if len(sanitized_title.encode('utf-8')) > max_title_bytes:
                # Truncate by bytes, not characters
                sanitized_title = sanitized_title.encode('utf-8')[:max_title_bytes].decode('utf-8', errors='ignore')
            # Build filename matching template
            file_name = f"{sanitized_title} [{video_id}].{'mp3' if self.ffmpeg_available else ext}"
        except (UnicodeEncodeError, UnicodeDecodeError, ValueError, AttributeError) as e:
            # Fallback to simple format if unicode sanitization fails
            logger.warning(f"Filename sanitization error, using fallback: {e}")
            file_name = f"{title[:100]} [{video_id}].{'mp3' if self.ffmpeg_available else ext}"
        except Exception:
            # CRITICAL: Unexpected error that should be investigated
            logger.exception("CRITICAL: Unexpected error in filename sanitization, using fallback")
            file_name = f"{title[:100]} [{video_id}].{'mp3' if self.ffmpeg_available else ext}"
        # Klasörün tam yolunu al
        output_dir = self.current_output_path or 'music'
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)
        
        file_info = {
            'title': title,
            'file_name': file_name,
            'file_path': output_dir,  # Klasörün tam yolu
            'format': 'mp3' if self.ffmpeg_available else ext,
            'url': info.get('webpage_url', info.get('url', '')),
            'file_size': info.get('filesize', 0),
            'duration': info.get('duration', 0),
            'channel': info.get('uploader', info.get('channel', '')),
            'video_id': video_id
        }
        
        # Add to database
        self.db_manager.add_download(file_info)
        
        # Mark as saved (thread-safe)
        with self._lock:
            self._saved_videos.add(video_id)
        
        # Check if this is part of a playlist
        if self.current_url in self.playlist_info:
            playlist_data = self.playlist_info[self.current_url]
            current_idx = self.current_playlist_index.get(self.current_url, 0) + 1
            self.current_playlist_index[self.current_url] = current_idx
            total_videos = playlist_data.get('count', 1)
            playlist_title = playlist_data.get('title', 'Playlist')
            
            # Log with playlist progress
            self.signals.status_update.emit(
                f"✅ [{current_idx}/{total_videos}] {playlist_title}: {title}"
            )
        # Also check info directly from yt-dlp
        elif info.get('playlist_index') and info.get('n_entries'):
            current_idx = info['playlist_index']
            total_videos = info['n_entries']
            playlist_title = info.get('playlist_title', info.get('playlist', 'Playlist'))
            
            # Log with playlist progress
            self.signals.status_update.emit(
                f"✅ [{current_idx}/{total_videos}] {playlist_title}: {title}"
            )
        else:
            # Log individual video
            self.signals.status_update.emit(translation_manager.tr('downloader.status.saved').format(title=title))
    
    def postprocessor_hook(self, d: Dict[str, Any]) -> None:
        """Hook for FFmpeg post-processing progress updates

        Args:
            d: Progress dictionary from yt-dlp containing:
                - status: Current status ('started', 'processing', 'finished')
                - info_dict: Video metadata including playlist information

        Emits status updates for MP3 conversion progress with playlist
        context when applicable.
        """
        # Check if this is part of a playlist
        status_prefix = ""
        # First check our tracked values from logger
        if self.current_item_index > 0 and self.playlist_total > 0:
            status_prefix = f"[{self.current_item_index}/{self.playlist_total}] "
        elif self.current_url in self.playlist_info:
            playlist_data = self.playlist_info[self.current_url]
            current_idx = self.current_playlist_index.get(self.current_url, 0) + 1
            total_videos = playlist_data.get('count', 1)
            status_prefix = f"[{current_idx}/{total_videos}] "
        # Also check info_dict for playlist info
        elif 'info_dict' in d and d['info_dict'].get('playlist_index') and d['info_dict'].get('n_entries'):
            current_idx = d['info_dict']['playlist_index']
            total_videos = d['info_dict']['n_entries']
            status_prefix = f"[{current_idx}/{total_videos}] "
            
        if d['status'] == 'started':
            self.signals.status_update.emit(f"🔄 {status_prefix}MP3'e dönüştürülüyor...")
        elif d['status'] == 'processing':
            self.signals.status_update.emit(f"🔄 {status_prefix}Dönüştürme devam ediyor...")
        elif d['status'] == 'finished':
            self.signals.status_update.emit(f"✨ {status_prefix}Dönüştürme tamamlandı!")
    
    def download_progress_hook(self, d: Dict[str, Any]) -> None:
        """Track download progress and emit status updates

        Args:
            d: Progress dictionary from yt-dlp containing:
                - status: Download status ('downloading', 'finished', 'error')
                - filename: Current file being downloaded
                - downloaded_bytes: Bytes downloaded so far
                - total_bytes: Total file size in bytes (if known)
                - info_dict: Video metadata including playlist information

        Raises:
            yt_dlp.DownloadError: When download is cancelled via is_running flag

        Tracks temporary files for cleanup and emits real-time progress
        updates with playlist context. Handles cancellation by raising
        DownloadError to interrupt yt-dlp processing.
        """
        # Track temp files for cleanup
        if 'filename' in d:
            with self._lock:
                self._current_temp_files.add(d['filename'])

        # İptal kontrolü
        if not self.is_running:
            # P0-3 FIX: Use centralized cleanup with proper error handling
            if 'filename' in d:
                logger.info(f"Download cancelled, cleaning up: {os.path.basename(d['filename'])}")
                self._cleanup_temp_files(d['filename'])
            # Raise DownloadError to stop the download
            raise yt_dlp.DownloadError(translation_manager.tr('downloader.errors.download_cancelled'))

        if d['status'] == 'downloading':
            filename = os.path.basename(d['filename'])
            
            # Check if this is part of a playlist
            status_prefix = ""
            # First check our tracked values from logger
            if self.current_item_index > 0 and self.playlist_total > 0:
                status_prefix = f"[{self.current_item_index}/{self.playlist_total}] "
            # Check if this is part of a playlist via URL tracking
            elif self.current_url in self.playlist_info:
                playlist_data = self.playlist_info[self.current_url]
                current_idx = self.current_playlist_index.get(self.current_url, 0) + 1
                total_videos = playlist_data.get('count', 1)
                status_prefix = f"[{current_idx}/{total_videos}] "
            # Also check info_dict for playlist info
            elif 'info_dict' in d and d['info_dict'].get('playlist_index') and d['info_dict'].get('n_entries'):
                current_idx = d['info_dict']['playlist_index']
                total_videos = d['info_dict']['n_entries']
                status_prefix = f"[{current_idx}/{total_videos}] "
                # Update our tracking
                if self.current_url:
                    self.current_playlist_index[self.current_url] = current_idx - 1
            
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                progress_text = f"{status_prefix}%{percent:.1f}" if status_prefix else f"%{percent:.1f}"
                self.signals.progress.emit(filename, percent, progress_text)
                self.signals.status_update.emit(f"📥 {status_prefix}İndiriliyor: {filename} - %{percent:.1f}")
            else:
                mb_downloaded = d['downloaded_bytes']/1024/1024
                progress_text = f"{status_prefix}{mb_downloaded:.1f} MB" if status_prefix else f"{mb_downloaded:.1f} MB"
                self.signals.progress.emit(filename, -1, progress_text)
                self.signals.status_update.emit(f"📥 {status_prefix}İndiriliyor: {filename} - {mb_downloaded:.1f} MB")
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            # Check playlist info for finished status
            status_prefix = ""
            # First check our tracked values from logger
            if self.current_item_index > 0 and self.playlist_total > 0:
                status_prefix = f"[{self.current_item_index}/{self.playlist_total}] "
            elif 'info_dict' in d and d['info_dict'].get('playlist_index') and d['info_dict'].get('n_entries'):
                current_idx = d['info_dict']['playlist_index']
                total_videos = d['info_dict']['n_entries']
                status_prefix = f"[{current_idx}/{total_videos}] "
            
            if filename.endswith('.webm') or filename.endswith('.m4a') or filename.endswith('.opus'):
                self.signals.status_update.emit(f"✅ {status_prefix}İndirme tamamlandı, MP3'e dönüştürülüyor...")
            else:
                self.signals.finished.emit(filename)
            
            # Save each video to database when download finishes
            if 'info_dict' in d:
                self.save_to_database(d['info_dict'])
        elif d['status'] == 'error':
            filename = os.path.basename(d.get('filename', 'Bilinmeyen dosya'))
            self.signals.error.emit(filename, str(d.get('error', 'Bilinmeyen hata')))

    def process_url(self, url: str, output_path: str) -> bool:
        """Process a YouTube URL and download as MP3

        Args:
            url: YouTube video or playlist URL to download
            output_path: Directory path to save downloaded files

        Returns:
            True if download completed successfully, False on error or cancellation

        Handles both single videos and playlists. Uses FFmpeg for MP3 conversion
        when available, otherwise downloads in original format. Implements
        proper error handling, timeout configuration, and cancellation support.
        """
        self.current_url = url
        self.current_output_path = output_path
        self.signals.status_update.emit(translation_manager.tr('downloader.status.checking_url').format(url=url))
        
        # yt-dlp seçenekleri
        if self.ffmpeg_available:
            # FFmpeg varsa MP3'e dönüştür
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'postprocessor_hooks': [self.postprocessor_hook],
                # SECURITY FIX: Sanitize filenames for cross-platform compatibility
                # Use .200B to limit length, include %(id)s for uniqueness (prevents same-title overwrites)
                'outtmpl': os.path.join(output_path, '%(title).200B [%(id)s].%(ext)s'),
                'windowsfilenames': True,  # Remove Windows-illegal characters (: < > | etc)
                'restrictfilenames': False,  # Keep unicode chars but sanitize via windowsfilenames
                'ignoreerrors': False,  # Don't ignore errors for better control
                'noplaylist': False,
                'progress_hooks': [self.download_progress_hook],
                'prefer_ffmpeg': True,
                'continuedl': False,  # Don't continue partial downloads
                'noprogress': False,
                'logger': self,  # Use self as logger to capture messages
                # P1-6 FIX: Add timeout and retry configuration
                'socket_timeout': 30,  # Socket timeout in seconds
                'retries': 3,  # Number of retries on connection failure
                'fragment_retries': 3,  # Number of retries for a fragment
            }
        else:
            # FFmpeg yoksa orijinal formatta indir
            ydl_opts = {
                'format': 'bestaudio/best',
                # SECURITY FIX: Sanitize filenames for cross-platform compatibility
                'outtmpl': os.path.join(output_path, '%(title).200B [%(id)s].%(ext)s'),
                'windowsfilenames': True,  # Remove Windows-illegal characters
                'restrictfilenames': False,  # Keep unicode chars
                'ignoreerrors': False,  # Don't ignore errors for better control
                'noplaylist': False,
                'progress_hooks': [self.download_progress_hook],
                'continuedl': False,  # Don't continue partial downloads
                'logger': self,  # Use self as logger to capture messages
                # P1-6 FIX: Add timeout and retry configuration
                'socket_timeout': 30,  # Socket timeout in seconds
                'retries': 3,  # Number of retries on connection failure
                'fragment_retries': 3,  # Number of retries for a fragment
            }
            self.signals.status_update.emit(translation_manager.tr('downloader.warnings.ffmpeg_not_found_fallback'))
        
        try:
            self.ydl = yt_dlp.YoutubeDL(ydl_opts)
            with self.ydl as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    # Check if this is a playlist
                    if info.get('_type') == 'playlist':
                        # Playlist - individual videos are saved via hooks
                        playlist_title = info.get('title', 'İsimsiz Playlist')
                        entry_count = len(info.get('entries', []))
                        
                        # Store playlist info
                        self.playlist_info[url] = {
                            'title': playlist_title,
                            'count': entry_count
                        }
                        self.current_playlist_index[url] = 0
                        
                        self.signals.status_update.emit(f"📋 Playlist başlatıldı: {playlist_title} ({entry_count} video)")
                    else:
                        # Single video - save to database if not already saved by hooks
                        title = info.get('title', 'Unknown')
                        # Save to database (duplicate check is in save_to_database)
                        self.save_to_database(info)
                        
                        if not self.ffmpeg_available:
                            ext = info.get('ext', 'webm')
                            self.signals.status_update.emit(f"✅ İndirildi: {title}.{ext} (MP3 dönüşümü için FFmpeg gerekli)")
                        else:
                            self.signals.status_update.emit(f"✅ İşlem tamamlandı: {title}.mp3")
                            self.signals.finished.emit(f"{title}.mp3")
                else:
                    self.signals.status_update.emit(f"✅ İndirme tamamlandı")
            self.ydl = None  # Clear the reference
            return True
        except yt_dlp.DownloadError as e:
            cancelled_msg = translation_manager.tr('downloader.errors.download_cancelled')
            if cancelled_msg in str(e):
                self.signals.status_update.emit(cancelled_msg)
            else:
                self.signals.error.emit(url, str(e))
                self.signals.status_update.emit(f"İndirme hatası: {e}")
            return False
        except KeyboardInterrupt:
            self.signals.status_update.emit("İndirme kullanıcı tarafından durduruldu")
            return False
        except (OSError, IOError) as e:
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"Dosya sistem hatası: {e}")
            return False
        except Exception as e:  # pylint: disable=broad-except
            # Beklenmeyen hatalar için fallback
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"Beklenmeyen hata: {e}")
            return False
        finally:
            self.ydl = None  # Always clear the reference
            self.current_item_index = 0
            self.playlist_total = 0

    def download_all(self, urls: List[str], output_path: str) -> None:
        """Download all URLs sequentially

        Args:
            urls: List of YouTube video or playlist URLs to download
            output_path: Directory path to save all downloaded files

        Processes each URL in sequence, maintaining proper state management
        and cleanup between downloads. Creates output directory if needed.
        Handles cancellation gracefully by checking is_running flag between
        downloads. Emits appropriate completion or cancellation messages.
        """
        self.is_running = True

        # P0-3 FIX: Reset temp files tracking along with other state
        with self._lock:
            self._saved_videos = set()
            self._current_temp_files = set()
        self.playlist_info = {}
        self.current_playlist_index = {}
        
        # Çıktı dizinini oluştur
        os.makedirs(output_path, exist_ok=True)
        
        for i, url in enumerate(urls, 1):
            if not self.is_running:
                self.signals.status_update.emit(translation_manager.tr("main.status.download_stopped"))
                break

            self.signals.status_update.emit(translation_manager.tr('downloader.status.processing_url_progress').format(current=i, total=len(urls)))
            success = self.process_url(url, output_path)

            if not success:
                # If cancelled, stop all downloads
                if not self.is_running:
                    self.signals.status_update.emit(translation_manager.tr("main.status.download_cancelled"))
                    break

        # Check if it was cancelled
        was_cancelled = not self.is_running
        self.is_running = False

        # Show appropriate final message
        if was_cancelled:
            self.signals.status_update.emit(translation_manager.tr("main.status.download_cancelled"))
        else:
            self.signals.status_update.emit(translation_manager.tr("main.status.all_downloads_completed"))

    def stop(self) -> None:
        """Stop the current download operation

        Sets the is_running flag to False to trigger cancellation in
        download_progress_hook. Attempts to set yt-dlp internal flags
        for faster cancellation. Performs cleanup of all temporary files
        created during download.

        Thread-safe operation that can be called from any thread.
        """
        logger.info("Stop requested - setting is_running to False")
        self.is_running = False

        # P0-3 FIX: Proper error handling when cancelling yt-dlp
        if self.ydl:
            try:
                # Force stop by setting internal flags
                if hasattr(self.ydl, 'params'):
                    self.ydl.params['break_on_reject'] = True
                    self.ydl.params['ignoreerrors'] = False
                    logger.debug("Set yt-dlp cancellation flags")
            except AttributeError as e:
                logger.warning(f"Could not set yt-dlp params (no params attribute): {e}")
            except Exception:
                logger.exception("Unexpected error setting yt-dlp cancellation flags")

        # P0-3 FIX: Use centralized cleanup with proper error handling
        logger.info("Starting temp file cleanup")
        self._cleanup_temp_files()  # Clean all tracked temp files

        self.signals.status_update.emit(translation_manager.tr('downloader.status.cancelling'))