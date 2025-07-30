import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    """İndirme geçmişi veritabanı yöneticisi"""
    
    def __init__(self, db_path: str = "mp3yap.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_db(self):
        """init_database için alias"""
        self.init_database()
    
    def init_database(self):
        """Veritabanını ve tabloları oluştur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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
                    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # İndirme kuyruğu tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    video_title TEXT,
                    format TEXT DEFAULT 'mp3',
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME,
                    completed_at DATETIME,
                    error_message TEXT,
                    position INTEGER
                )
            ''')
            
            # İndeksler
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
            
            conn.commit()
    
    def add_download(self, video_info: Dict) -> int:
        """Yeni indirme kaydı ekle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO download_history 
                (video_title, file_name, file_path, format, url, 
                 file_size, duration, channel_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_info.get('title', 'Unknown'),
                video_info.get('file_name', ''),
                video_info.get('file_path', ''),
                video_info.get('format', 'mp3'),
                video_info.get('url', ''),
                video_info.get('file_size', 0),
                video_info.get('duration', 0),
                video_info.get('channel', '')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_downloads(self, limit: int = 100) -> List[Dict]:
        """Tüm indirme geçmişini getir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_history 
                ORDER BY downloaded_at DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def search_downloads(self, query: str) -> List[Dict]:
        """İndirme geçmişinde arama yap"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_history 
                WHERE video_title LIKE ? OR channel_name LIKE ?
                ORDER BY downloaded_at DESC
            ''', (f'%{query}%', f'%{query}%'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """İndirme istatistiklerini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Toplam indirme sayısı
            cursor.execute('SELECT COUNT(*) FROM download_history')
            total_downloads = cursor.fetchone()[0]
            
            # Toplam dosya boyutu
            cursor.execute('SELECT SUM(file_size) FROM download_history')
            total_size = cursor.fetchone()[0] or 0
            
            # En çok indirilen kanal
            cursor.execute('''
                SELECT channel_name, COUNT(*) as count 
                FROM download_history 
                WHERE channel_name IS NOT NULL AND channel_name != ''
                GROUP BY channel_name 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            top_channels = cursor.fetchall()
            
            # Bugünkü indirmeler
            cursor.execute('''
                SELECT COUNT(*) FROM download_history 
                WHERE DATE(downloaded_at) = DATE('now', 'localtime')
            ''')
            today_downloads = cursor.fetchone()[0]
            
            return {
                'total_downloads': total_downloads,
                'total_size_mb': total_size / (1024 * 1024) if total_size else 0,
                'top_channels': top_channels,
                'today_downloads': today_downloads
            }
    
    def delete_download(self, download_id: int) -> bool:
        """İndirme kaydını sil"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM download_history WHERE id = ?', (download_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_history(self) -> int:
        """Tüm geçmişi temizle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM download_history')
            conn.commit()
            return cursor.rowcount
    
    # Kuyruk yönetimi metodları
    
    def add_to_queue(self, url: str, video_title: Optional[str] = None, 
                     format: str = 'mp3', priority: int = 0) -> int:
        """Kuyruğa yeni indirme ekle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Mevcut maksimum pozisyonu bul
            cursor.execute('SELECT MAX(position) FROM download_queue')
            max_pos = cursor.fetchone()[0]
            next_pos = (max_pos or 0) + 1
            
            cursor.execute('''
                INSERT INTO download_queue 
                (url, video_title, format, priority, position)
                VALUES (?, ?, ?, ?, ?)
            ''', (url, video_title, format, priority, next_pos))
            
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_queue_items(self, status: Optional[str] = None) -> List[Dict]:
        """Kuyruktaki öğeleri getir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM download_queue 
                    WHERE status = ?
                    ORDER BY priority DESC, position ASC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT * FROM download_queue 
                    ORDER BY priority DESC, position ASC
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_queue_status(self, queue_id: int, status: str, 
                           error_message: Optional[str] = None) -> bool:
        """Kuyruk öğesinin durumunu güncelle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if status == 'downloading':
                cursor.execute('''
                    UPDATE download_queue 
                    SET status = ?, started_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, queue_id))
            elif status == 'completed':
                cursor.execute('''
                    UPDATE download_queue 
                    SET status = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, queue_id))
            elif status == 'failed':
                cursor.execute('''
                    UPDATE download_queue 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                ''', (status, error_message, queue_id))
            else:
                cursor.execute('''
                    UPDATE download_queue 
                    SET status = ?
                    WHERE id = ?
                ''', (status, queue_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_queue_position(self, queue_id: int, new_position: int) -> bool:
        """Kuyruk öğesinin pozisyonunu güncelle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_queue 
                SET position = ?
                WHERE id = ?
            ''', (new_position, queue_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def remove_from_queue(self, queue_id: int) -> bool:
        """Kuyruktan öğe sil"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM download_queue WHERE id = ?', (queue_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_queue(self, status: Optional[str] = None) -> int:
        """Kuyruğu temizle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('DELETE FROM download_queue WHERE status = ?', (status,))
            else:
                cursor.execute('DELETE FROM download_queue')
            conn.commit()
            return cursor.rowcount
    
    def get_next_queue_item(self) -> Optional[Dict]:
        """Sıradaki indirme öğesini getir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_queue 
                WHERE status = 'pending'
                ORDER BY priority DESC, position ASC
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None