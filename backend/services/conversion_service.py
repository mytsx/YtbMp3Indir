"""
Conversion Service
Handles local file conversion to MP3 with FFmpeg
Thread-safe job queue pattern from TTS/Download service
"""
import asyncio
import os
import uuid
import logging
import threading
import queue
import subprocess
import re
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Global conversion service instance
_conversion_service = None


class Conversion:
    """Conversion tracking object"""

    def __init__(self, conversion_id: str, input_path: str, quality: str = "192"):
        self.id = conversion_id
        self.input_path = input_path
        self.quality = quality
        self.status = "pending"  # pending, converting, completed, failed, cancelled
        self.progress = 0  # 0-100
        self.output_path = None
        self.file_name = os.path.basename(input_path)
        self.error = None
        self.created_at = datetime.now()
        self.duration = None  # Total duration in seconds
        self.current_time = None  # Current processed time
        self.process = None  # FFmpeg process handle for cancellation

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "file_name": self.file_name,
            "status": self.status,
            "progress": self.progress,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "duration": self.duration,
        }


class ConversionService:
    """Service for managing file conversions with thread-safe job queue"""

    def __init__(self, output_dir: str = "./music", max_workers: int = 2):
        self.output_dir = os.path.abspath(output_dir)
        self.active_conversions: Dict[str, Conversion] = {}
        self.websocket_manager = None

        # Thread-safe job queue
        self.job_queue = queue.Queue()
        self.conversions_lock = threading.Lock()
        self.shutdown_event = threading.Event()

        # Worker threads
        self.max_workers = max_workers
        self.workers = []
        self._start_workers()

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def _start_workers(self):
        """Start worker threads for processing conversion jobs"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"ConversionWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        logger.info(f"Started {self.max_workers} conversion worker threads")

    def _worker_loop(self):
        """Worker thread main loop"""
        while not self.shutdown_event.is_set():
            try:
                conversion = self.job_queue.get(timeout=1)
                asyncio.run(self._conversion_worker(conversion))
                self.job_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.exception(f"Conversion worker error: {e}")

    def shutdown(self):
        """Graceful shutdown of worker threads"""
        logger.info("Shutting down conversion service...")
        self.shutdown_event.set()
        for worker in self.workers:
            worker.join(timeout=5)
        logger.info("Conversion service shutdown complete")

    def set_websocket_manager(self, manager):
        """Inject WebSocket manager for progress updates"""
        self.websocket_manager = manager

    async def broadcast_progress(self, conversion_id: str, message: dict):
        """Broadcast progress update via WebSocket"""
        if self.websocket_manager:
            await self.websocket_manager.broadcast(conversion_id, message)

    async def start_conversion(self, input_path: str, quality: str = "192") -> Conversion:
        """Start a new conversion"""
        # Validate input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        conversion_id = str(uuid.uuid4())
        conversion = Conversion(conversion_id, input_path, quality)

        with self.conversions_lock:
            self.active_conversions[conversion_id] = conversion

        self.job_queue.put(conversion)
        logger.info(f"Queued conversion {conversion_id} for {input_path}")
        return conversion

    async def _conversion_worker(self, conversion: Conversion):
        """Background worker that performs the actual conversion"""
        try:
            conversion.status = "converting"
            await self.broadcast_progress(conversion.id, {
                "type": "status",
                "status": "converting",
                "message": "Starting conversion..."
            })

            # Get input file info
            input_path = conversion.input_path
            file_name = os.path.splitext(os.path.basename(input_path))[0]

            # Sanitize filename
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
            output_path = os.path.join(self.output_dir, f"{safe_name}.mp3")

            # Avoid overwriting - add number suffix if exists
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(self.output_dir, f"{safe_name}_{counter}.mp3")
                counter += 1

            conversion.output_path = output_path

            # Get duration first
            duration = await self._get_duration(input_path)
            conversion.duration = duration

            # Run FFmpeg conversion with progress
            await self._run_ffmpeg(conversion, input_path, output_path)

            # Conversion completed
            conversion.status = "completed"
            conversion.progress = 100

            await self.broadcast_progress(conversion.id, {
                "type": "completed",
                "status": "completed",
                "progress": 100,
                "output_path": output_path,
                "message": "Conversion completed!"
            })

            logger.info(f"Conversion {conversion.id} completed: {output_path}")

        except Exception as e:
            logger.exception(f"Conversion {conversion.id} failed: {e}")
            conversion.status = "failed"
            conversion.error = str(e)

            await self.broadcast_progress(conversion.id, {
                "type": "error",
                "status": "failed",
                "error": str(e),
                "message": f"Conversion failed: {str(e)}"
            })

    async def _get_duration(self, input_path: str) -> Optional[float]:
        """Get media file duration using ffprobe"""
        try:
            result = subprocess.run(
                [
                    'ffprobe', '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    input_path
                ],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
        return None

    async def _run_ffmpeg(self, conversion: Conversion, input_path: str, output_path: str):
        """Run FFmpeg with progress tracking"""
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-i', input_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ab', f'{conversion.quality}k',
            '-ar', '44100',
            '-progress', 'pipe:1',  # Progress to stdout
            output_path
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Store process handle for cancellation
        conversion.process = process

        # Parse progress output
        duration = conversion.duration or 0

        while True:
            # Check for cancellation
            if conversion.status == "cancelled":
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                # Clean up partial output file
                if output_path and os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass
                raise Exception("Conversion cancelled by user")

            line = await process.stdout.readline()
            if not line:
                break

            line = line.decode().strip()

            # Parse out_time for progress
            if line.startswith('out_time_ms='):
                try:
                    time_ms = int(line.split('=')[1])
                    current_seconds = time_ms / 1_000_000

                    if duration > 0:
                        progress = max(0, min(int((current_seconds / duration) * 100), 99))
                        conversion.progress = progress

                        await self.broadcast_progress(conversion.id, {
                            "type": "progress",
                            "progress": progress,
                        })
                except Exception:
                    pass

        await process.wait()

        # Clear process handle
        conversion.process = None

        if process.returncode != 0:
            stderr = await process.stderr.read()
            raise Exception(f"FFmpeg error: {stderr.decode()}")

    def get_conversion(self, conversion_id: str) -> Optional[Conversion]:
        """Get conversion by ID"""
        with self.conversions_lock:
            return self.active_conversions.get(conversion_id)

    def get_all_conversions(self):
        """Get all active conversions"""
        with self.conversions_lock:
            return list(self.active_conversions.values())

    async def cancel_conversion(self, conversion_id: str):
        """Cancel a conversion"""
        with self.conversions_lock:
            conversion = self.active_conversions.get(conversion_id)
            if conversion:
                conversion.status = "cancelled"
                # If process is running, it will be terminated in _run_ffmpeg
                logger.info(f"Conversion {conversion_id} cancelled")

                # Broadcast cancellation status
                await self.broadcast_progress(conversion_id, {
                    "type": "status",
                    "status": "cancelled",
                    "message": "Conversion cancelled"
                })


def get_conversion_service() -> ConversionService:
    """Get or create global conversion service instance"""
    global _conversion_service
    if _conversion_service is None:
        _conversion_service = ConversionService()
    return _conversion_service
