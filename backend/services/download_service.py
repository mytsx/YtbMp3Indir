"""
Download Service
Handles YouTube downloads with yt-dlp and progress tracking
Thread-safe job queue pattern from TTS
"""
import asyncio
import os
import uuid
import logging
import threading
import queue
from typing import Dict, Optional, Literal
from datetime import datetime
import yt_dlp
from database.manager import get_database_manager

# Audio quality type
AudioQuality = Literal["128", "192", "256", "320"]
DEFAULT_QUALITY: AudioQuality = "320"

logger = logging.getLogger(__name__)

# Global download service instance with thread-safe initialization
_download_service = None
_download_service_lock = threading.Lock()


class Download:
    """Download tracking object"""

    def __init__(self, download_id: str, url: str, quality: AudioQuality = DEFAULT_QUALITY):
        self.id = download_id
        self.url = url
        self.quality = quality
        self.status = "pending"  # pending, downloading, converting, completed, failed, cancelled
        self.progress = 0  # 0-100
        self.video_title = None
        self.file_path = None
        self.error = None
        self.created_at = datetime.now()
        self.speed = None
        self.eta = None

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "progress": self.progress,
            "video_title": self.video_title,
            "file_path": self.file_path,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "speed": self.speed,
            "eta": self.eta,
        }


class DownloadService:
    """Service for managing downloads with thread-safe job queue (TTS pattern)"""

    def __init__(self, output_dir: str = "./music", max_workers: int = 3):
        # Convert to absolute path to ensure compatibility with AudioPlayer
        self.output_dir = os.path.abspath(output_dir)
        self.active_downloads: Dict[str, Download] = {}
        self.websocket_manager = None  # Will be injected
        self.db_manager = get_database_manager()

        # Thread-safe job queue (TTS pattern)
        self.job_queue = queue.Queue()
        self.downloads_lock = threading.Lock()  # Protect active_downloads dict
        self.shutdown_event = threading.Event()

        # Worker threads for processing downloads
        self.max_workers = max_workers
        self.workers = []
        self._start_workers()

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def set_output_dir(self, output_dir: str):
        """Update output directory for downloads"""
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Download output directory set to: {self.output_dir}")

    def _start_workers(self):
        """Start worker threads for processing download jobs (TTS pattern)"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"DownloadWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        logger.info(f"Started {self.max_workers} download worker threads")

    def _worker_loop(self):
        """Worker thread main loop - processes jobs from queue (TTS pattern)"""
        while not self.shutdown_event.is_set():
            try:
                # Get job from queue with timeout to check shutdown periodically
                download = self.job_queue.get(timeout=1)

                # Process the download
                asyncio.run(self._download_worker(download))

                self.job_queue.task_done()
            except queue.Empty:
                continue  # Timeout - check shutdown and loop again
            except Exception as e:
                logger.exception(f"Worker thread error: {e}")

    def shutdown(self):
        """Graceful shutdown of worker threads (TTS pattern)"""
        logger.info("Shutting down download service...")
        self.shutdown_event.set()

        # Wait for all workers to finish
        for worker in self.workers:
            worker.join(timeout=5)

        logger.info("Download service shutdown complete")

    def set_websocket_manager(self, manager):
        """Inject WebSocket manager for progress updates"""
        self.websocket_manager = manager

    async def broadcast_progress(self, download_id: str, message: dict):
        """Broadcast progress update via WebSocket"""
        if self.websocket_manager:
            await self.websocket_manager.broadcast(download_id, message)

    async def start_download(self, url: str, quality: AudioQuality = DEFAULT_QUALITY) -> Download:
        """Start a new download - adds to thread-safe queue (TTS pattern)"""
        download_id = str(uuid.uuid4())
        download = Download(download_id, url, quality)

        # Thread-safe: Store in active downloads with lock
        with self.downloads_lock:
            self.active_downloads[download_id] = download

        # Add to job queue - worker threads will process it
        self.job_queue.put(download)

        logger.info(f"Queued download {download_id} for {url} (queue size: {self.job_queue.qsize()})")
        return download

    async def _download_worker(self, download: Download):
        """Background worker that performs the actual download"""
        try:
            download.status = "downloading"
            await self.broadcast_progress(download.id, {
                "type": "status",
                "status": "downloading",
                "message": "Starting download..."
            })

            # Get the event loop for progress hook
            loop = asyncio.get_event_loop()

            # Progress hook for yt-dlp
            def progress_hook(d):
                if d['status'] == 'downloading':
                    # Extract progress
                    try:
                        downloaded = d.get('downloaded_bytes', 0)
                        # Try total_bytes first, then estimate
                        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0

                        if downloaded and total:
                            progress = int((downloaded / total) * 100)
                        elif '_percent_str' in d:
                            # Parse percentage string like "50.0%"
                            progress_str = d['_percent_str'].strip().rstrip('%')
                            progress = int(float(progress_str))
                        else:
                            progress = download.progress  # Keep current

                        download.progress = min(progress, 99)  # Cap at 99 until complete

                        # Extract and format speed (ensure 2 decimal places)
                        speed_raw = d.get('speed')  # Bytes per second
                        if speed_raw and isinstance(speed_raw, (int, float)):
                            if speed_raw >= 1024 * 1024:
                                speed = f"{speed_raw / (1024 * 1024):.2f} MB/s"
                            elif speed_raw >= 1024:
                                speed = f"{speed_raw / 1024:.2f} KB/s"
                            else:
                                speed = f"{speed_raw:.0f} B/s"
                        else:
                            speed = d.get('_speed_str', 'N/A')

                        eta = d.get('_eta_str', 'N/A')

                        download.speed = speed
                        download.eta = eta

                        # Broadcast progress from executor thread to event loop
                        asyncio.run_coroutine_threadsafe(
                            self.broadcast_progress(download.id, {
                                "type": "progress",
                                "progress": download.progress,
                                "speed": speed,
                                "eta": eta
                            }),
                            loop
                        )

                    except Exception as e:
                        logger.error(f"Error parsing progress: {e}")

                elif d['status'] == 'finished':
                    download.status = "converting"
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_progress(download.id, {
                            "type": "status",
                            "status": "converting",
                            "message": "Converting to MP3..."
                        }),
                        loop
                    )

            # yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s [%(id)s].%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': download.quality,
                }],
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }

            # Perform download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to get title
                info = ydl.extract_info(download.url, download=False)
                download.video_title = info.get('title', 'Unknown')

                # Broadcast title
                await self.broadcast_progress(download.id, {
                    "type": "info",
                    "video_title": download.video_title
                })

                # Download
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ydl.download([download.url])
                )

            # Download completed
            download.status = "completed"
            download.progress = 100

            # Find the downloaded file using yt-dlp's sanitized filename
            video_id = info.get('id', '')

            # Use yt-dlp's prepare_filename to get the actual sanitized filename
            info['ext'] = 'mp3'  # Set extension for prepare_filename
            prepared_path = ydl.prepare_filename(info)
            # The extension might be different, ensure it's .mp3
            base_path = os.path.splitext(prepared_path)[0]
            download.file_path = base_path + '.mp3'

            # If file doesn't exist, try to find it by video ID pattern
            if not os.path.exists(download.file_path):
                import glob
                pattern = os.path.join(self.output_dir, f'*[{video_id}].mp3')
                matches = glob.glob(pattern)
                if matches:
                    download.file_path = matches[0]
                    logger.info(f"Found file by pattern: {download.file_path}")

            # Get file size
            file_size = None
            if os.path.exists(download.file_path):
                file_size = os.path.getsize(download.file_path)

            # Save to database
            try:
                video_info = {
                    'title': download.video_title,
                    'file_name': os.path.basename(download.file_path),
                    'file_path': download.file_path,
                    'format': 'mp3',
                    'url': download.url,
                    'file_size': file_size,
                    'duration': info.get('duration'),
                    'channel_name': info.get('uploader'),
                    'video_id': video_id,
                }
                await self.db_manager.add_download(video_info)
                logger.info(f"Download saved to database: {download.video_title}")
            except Exception as e:
                logger.error(f"Failed to save download to database: {e}")

            await self.broadcast_progress(download.id, {
                "type": "completed",
                "status": "completed",
                "progress": 100,
                "file_path": download.file_path,
                "message": "Download completed!"
            })

            logger.info(f"Download {download.id} completed: {download.file_path}")

        except Exception as e:
            logger.exception(f"Download {download.id} failed: {e}")
            download.status = "failed"
            download.error = str(e)

            await self.broadcast_progress(download.id, {
                "type": "error",
                "status": "failed",
                "error": str(e),
                "message": f"Download failed: {str(e)}"
            })

    def get_download(self, download_id: str) -> Optional[Download]:
        """Get download by ID - thread-safe"""
        with self.downloads_lock:
            return self.active_downloads.get(download_id)

    def get_all_downloads(self):
        """Get all active downloads - thread-safe"""
        with self.downloads_lock:
            return list(self.active_downloads.values())

    def cancel_download(self, download_id: str):
        """Cancel a download - thread-safe"""
        with self.downloads_lock:
            download = self.active_downloads.get(download_id)
            if download:
                download.status = "cancelled"
                # TODO: Actually cancel yt-dlp process
                logger.info(f"Download {download_id} cancelled")


def get_download_service() -> DownloadService:
    """Get or create global download service instance (thread-safe)"""
    global _download_service
    if _download_service is None:
        with _download_service_lock:
            # Double-checked locking pattern
            if _download_service is None:
                # Load output_dir from config
                from config_manager import get_config_manager
                config = get_config_manager()
                output_dir = config.get('output_dir', './music')
                _download_service = DownloadService(output_dir=output_dir)
    return _download_service
