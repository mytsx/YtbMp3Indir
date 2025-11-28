"""
Database Manager
SQLite database for download history and queue
"""
import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for async database operations
_executor = ThreadPoolExecutor(max_workers=3)


class DatabaseManager:
    """Download history and queue database manager"""

    def __init__(self, db_path: str = "mp3yap.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database and tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Download history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_title TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT,
                    format TEXT DEFAULT 'mp3',
                    url TEXT NOT NULL,
                    file_size INTEGER,
                    duration INTEGER,
                    channel_name TEXT,
                    video_id TEXT,
                    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    is_deleted INTEGER DEFAULT 0
                )
            ''')

            # Download queue table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    video_title TEXT,
                    video_id TEXT,
                    format TEXT DEFAULT 'mp3',
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME,
                    completed_at DATETIME,
                    error_message TEXT,
                    position INTEGER,
                    is_deleted INTEGER DEFAULT 0
                )
            ''')

            # Indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_downloaded_at
                ON download_history(downloaded_at DESC)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_video_title
                ON download_history(video_title)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_queue_status
                ON download_queue(status)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_queue_position
                ON download_queue(position)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_is_deleted
                ON download_history(is_deleted)
            ''')

            conn.commit()
            logger.info(f"Database initialized: {self.db_path}")

    def _add_download_sync(self, video_info: Dict) -> int:
        """Add download to history (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO download_history
                (video_title, file_name, file_path, format, url,
                 file_size, duration, channel_name, video_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_info.get('title', 'Unknown'),
                video_info.get('file_name', ''),
                video_info.get('file_path', ''),
                video_info.get('format', 'mp3'),
                video_info.get('url', ''),
                video_info.get('file_size'),
                video_info.get('duration'),
                video_info.get('channel_name'),
                video_info.get('video_id'),
            ))
            conn.commit()
            return cursor.lastrowid or 0

    async def add_download(self, video_info: Dict) -> int:
        """Add download to history (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._add_download_sync, video_info)

    def _get_history_sync(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get download history (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_history
                WHERE is_deleted = 0
                ORDER BY downloaded_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get download history (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._get_history_sync, limit, offset)

    def _get_history_item_sync(self, history_id: int) -> Optional[Dict]:
        """Get specific history item (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_history
                WHERE id = ? AND is_deleted = 0
            ''', (history_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

    async def get_history_item(self, history_id: int) -> Optional[Dict]:
        """Get specific history item (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._get_history_item_sync, history_id)

    def _delete_history_item_sync(self, history_id: int) -> bool:
        """Soft delete history item (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_history
                SET is_deleted = 1
                WHERE id = ?
            ''', (history_id,))
            conn.commit()
            return cursor.rowcount > 0

    async def delete_history_item(self, history_id: int) -> bool:
        """Soft delete history item (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._delete_history_item_sync, history_id)

    def _get_statistics_sync(self) -> Dict:
        """Get download statistics (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total downloads
            cursor.execute('''
                SELECT COUNT(*) FROM download_history
                WHERE is_deleted = 0
            ''')
            total_downloads = cursor.fetchone()[0]

            # Total size
            cursor.execute('''
                SELECT SUM(file_size) FROM download_history
                WHERE is_deleted = 0 AND file_size IS NOT NULL
            ''')
            total_size = cursor.fetchone()[0] or 0

            # Total duration
            cursor.execute('''
                SELECT SUM(duration) FROM download_history
                WHERE is_deleted = 0 AND duration IS NOT NULL
            ''')
            total_duration = cursor.fetchone()[0] or 0

            return {
                'total_downloads': total_downloads,
                'total_size': total_size,
                'total_duration': total_duration,
            }

    async def get_statistics(self) -> Dict:
        """Get download statistics (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._get_statistics_sync)

    def _search_history_sync(self, query: str) -> List[Dict]:
        """Search history by video title (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_history
                WHERE is_deleted = 0 AND video_title LIKE ?
                ORDER BY downloaded_at DESC
                LIMIT 50
            ''', (f'%{query}%',))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def search_history(self, query: str) -> List[Dict]:
        """Search history by video title (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._search_history_sync, query)

    def _cleanup_old_history_sync(self, retention_days: int) -> int:
        """Delete history items older than retention_days (sync)"""
        if retention_days <= 0:
            return 0  # 0 or negative means keep forever

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_history
                SET is_deleted = 1
                WHERE is_deleted = 0
                AND datetime(downloaded_at) < datetime('now', '-' || ? || ' days')
            ''', (retention_days,))
            conn.commit()
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} history items older than {retention_days} days")
            return deleted_count

    async def cleanup_old_history(self, retention_days: int) -> int:
        """Delete history items older than retention_days (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._cleanup_old_history_sync, retention_days)

    # ==========================================================================
    # Queue Management
    # ==========================================================================

    def _get_queue_sync(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get download queue (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_queue
                WHERE is_deleted = 0
                ORDER BY priority DESC, position ASC, added_at ASC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_queue(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get download queue (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._get_queue_sync, limit, offset)

    def _add_to_queue_sync(self, url: str, priority: int = 0) -> int:
        """Add item to queue (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get next position
            cursor.execute('SELECT MAX(position) FROM download_queue WHERE is_deleted = 0')
            max_pos = cursor.fetchone()[0]
            position = (max_pos or -1) + 1

            cursor.execute('''
                INSERT INTO download_queue
                (url, priority, position, status)
                VALUES (?, ?, ?, 'pending')
            ''', (url, priority, position))

            conn.commit()
            return cursor.lastrowid or 0

    async def add_to_queue(self, url: str, priority: int = 0) -> int:
        """Add item to queue (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._add_to_queue_sync, url, priority)

    def _get_queue_item_sync(self, queue_id: int) -> Optional[Dict]:
        """Get specific queue item (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_queue
                WHERE id = ? AND is_deleted = 0
            ''', (queue_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

    async def get_queue_item(self, queue_id: int) -> Optional[Dict]:
        """Get specific queue item (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._get_queue_item_sync, queue_id)

    def _update_queue_priority_sync(self, queue_id: int, priority: int) -> bool:
        """Update queue item priority (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_queue
                SET priority = ?
                WHERE id = ? AND is_deleted = 0
            ''', (priority, queue_id))
            conn.commit()
            return cursor.rowcount > 0

    async def update_queue_priority(self, queue_id: int, priority: int) -> bool:
        """Update queue item priority (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._update_queue_priority_sync, queue_id, priority)

    def _update_queue_position_sync(self, queue_id: int, position: int) -> bool:
        """Update queue item position (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_queue
                SET position = ?
                WHERE id = ? AND is_deleted = 0
            ''', (position, queue_id))
            conn.commit()
            return cursor.rowcount > 0

    async def update_queue_position(self, queue_id: int, position: int) -> bool:
        """Update queue item position (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._update_queue_position_sync, queue_id, position)

    def _delete_queue_item_sync(self, queue_id: int) -> bool:
        """Soft delete queue item (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_queue
                SET is_deleted = 1
                WHERE id = ?
            ''', (queue_id,))
            conn.commit()
            return cursor.rowcount > 0

    async def delete_queue_item(self, queue_id: int) -> bool:
        """Soft delete queue item (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._delete_queue_item_sync, queue_id)

    def _clear_queue_sync(self, status: str = "all") -> int:
        """Clear queue items by status (sync)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if status == "all":
                cursor.execute('''
                    UPDATE download_queue
                    SET is_deleted = 1
                    WHERE is_deleted = 0
                ''')
            else:
                cursor.execute('''
                    UPDATE download_queue
                    SET is_deleted = 1
                    WHERE is_deleted = 0 AND status = ?
                ''', (status,))

            conn.commit()
            return cursor.rowcount

    async def clear_queue(self, status: str = "all") -> int:
        """Clear queue items by status (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._clear_queue_sync, status)


# Global database manager instance
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get or create global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
