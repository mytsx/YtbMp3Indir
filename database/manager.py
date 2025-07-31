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
    
    def _add_is_deleted_columns(self, cursor):
        """Mevcut tablolara is_deleted sütununu ekle"""
        try:
            # download_history tablosuna is_deleted ekle
            cursor.execute("PRAGMA table_info(download_history)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'is_deleted' not in columns:
                cursor.execute('ALTER TABLE download_history ADD COLUMN is_deleted INTEGER DEFAULT 0')
            
            # download_queue tablosuna is_deleted ekle
            cursor.execute("PRAGMA table_info(download_queue)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'is_deleted' not in columns:
                cursor.execute('ALTER TABLE download_queue ADD COLUMN is_deleted INTEGER DEFAULT 0')
        except:
            # Tablo yoksa veya başka bir hata varsa sessizce geç
            pass
    
    def _add_video_id_columns(self, cursor):
        """Mevcut tablolara video_id sütununu ekle"""
        try:
            # download_queue tablosuna video_id ekle
            cursor.execute("PRAGMA table_info(download_queue)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'video_id' not in columns:
                cursor.execute('ALTER TABLE download_queue ADD COLUMN video_id TEXT')
            
            # download_history tablosuna video_id ekle
            cursor.execute("PRAGMA table_info(download_history)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'video_id' not in columns:
                cursor.execute('ALTER TABLE download_history ADD COLUMN video_id TEXT')
        except:
            pass
    
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
                    status TEXT DEFAULT 'completed',
                    is_deleted INTEGER DEFAULT 0
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
                    position INTEGER,
                    is_deleted INTEGER DEFAULT 0
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
            
            # Mevcut tablolara is_deleted sütununu ekle (migration)
            self._add_is_deleted_columns(cursor)
            # video_id sütununu ekle
            self._add_video_id_columns(cursor)
            conn.commit()
    
    def add_download(self, video_info: Dict) -> int:
        """Yeni indirme kaydı ekle"""
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
                video_info.get('file_size', 0),
                video_info.get('duration', 0),
                video_info.get('channel', ''),
                video_info.get('video_id', '')
            ))
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_all_downloads(self, limit: int = 100, include_deleted: bool = False) -> List[Dict]:
        """Tüm indirme geçmişini getir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if include_deleted:
                cursor.execute('''
                    SELECT * FROM download_history 
                    ORDER BY downloaded_at DESC 
                    LIMIT ?
                ''', (limit,))
            else:
                cursor.execute('''
                    SELECT * FROM download_history 
                    WHERE is_deleted = 0
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
                WHERE (video_title LIKE ? OR channel_name LIKE ? OR url LIKE ?)
                AND is_deleted = 0
                ORDER BY downloaded_at DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_download_by_url(self, url: str) -> List[Dict]:
        """URL ile tam eşleşen indirmeleri getir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_history 
                WHERE url = ? AND is_deleted = 0
                ORDER BY downloaded_at DESC
            ''', (url,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """İndirme istatistiklerini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Toplam indirme sayısı
            cursor.execute('SELECT COUNT(*) FROM download_history WHERE is_deleted = 0')
            total_downloads = cursor.fetchone()[0]
            
            # Toplam dosya boyutu
            cursor.execute('SELECT SUM(file_size) FROM download_history WHERE is_deleted = 0')
            total_size = cursor.fetchone()[0] or 0
            
            # En çok indirilen kanal
            cursor.execute('''
                SELECT channel_name, COUNT(*) as count 
                FROM download_history 
                WHERE channel_name IS NOT NULL AND channel_name != '' AND is_deleted = 0
                GROUP BY channel_name 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            top_channels = cursor.fetchall()
            
            # Bugünkü indirmeler
            cursor.execute('''
                SELECT COUNT(*) FROM download_history 
                WHERE DATE(downloaded_at) = DATE('now', 'localtime') AND is_deleted = 0
            ''')
            today_downloads = cursor.fetchone()[0]
            
            return {
                'total_downloads': total_downloads,
                'total_size_mb': total_size / (1024 * 1024) if total_size else 0,
                'top_channels': top_channels,
                'today_downloads': today_downloads
            }
    
    def delete_download(self, download_id: int) -> bool:
        """İndirme kaydını soft delete yap"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE download_history SET is_deleted = 1 WHERE id = ?', (download_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def hard_delete_download(self, download_id: int) -> bool:
        """İndirme kaydını kalıcı olarak sil"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM download_history WHERE id = ?', (download_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def restore_download(self, download_id: int) -> bool:
        """Silinmiş indirme kaydını geri getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE download_history SET is_deleted = 0 WHERE id = ?', (download_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_history(self) -> int:
        """Tüm geçmişi soft delete yap"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE download_history SET is_deleted = 1 WHERE is_deleted = 0')
            conn.commit()
            return cursor.rowcount
    
    def hard_clear_history(self) -> int:
        """Tüm geçmişi kalıcı olarak sil"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM download_history')
            conn.commit()
            return cursor.rowcount
    
    # Kuyruk yönetimi metodları
    
    def add_to_queue(self, url: str, video_title: Optional[str] = None, 
                     format: str = 'mp3', priority: int = 0) -> int:
        """Kuyruğa yeni indirme ekle"""
        from utils.youtube_utils import extract_video_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Video ID'yi çıkar
            video_id = extract_video_id(url)
            
            if video_id:
                # Video ID ile kontrol et (sadece aktif kayıtlar)
                cursor.execute('''
                    SELECT id, status, url FROM download_queue 
                    WHERE video_id = ? AND is_deleted = 0 AND status != 'completed'
                ''', (video_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Aynı video zaten kuyrukta
                    return -1  # Duplicate olduğunu belirtmek için -1 döndür
            else:
                # Video ID çıkarılamadı, URL ile kontrol et
                cursor.execute('''
                    SELECT id, status FROM download_queue 
                    WHERE url = ? AND is_deleted = 0 AND status != 'completed'
                ''', (url,))
                existing = cursor.fetchone()
                
                if existing:
                    return -1
            
            # Mevcut maksimum pozisyonu bul
            cursor.execute('SELECT MAX(position) FROM download_queue WHERE is_deleted = 0')
            max_pos = cursor.fetchone()[0]
            next_pos = (max_pos or 0) + 1
            
            cursor.execute('''
                INSERT INTO download_queue 
                (url, video_title, format, priority, position, video_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, video_title, format, priority, next_pos, video_id))
            
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
                    WHERE status = ? AND is_deleted = 0
                    ORDER BY priority DESC, position ASC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT * FROM download_queue 
                    WHERE is_deleted = 0
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
    
    def remove_from_queue(self, queue_id: int) -> bool:
        """Kuyruktan öğe soft delete yap"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE download_queue SET is_deleted = 1 WHERE id = ?', (queue_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_queue(self, status: Optional[str] = None) -> int:
        """Kuyruğu soft delete yap"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('UPDATE download_queue SET is_deleted = 1 WHERE status = ? AND is_deleted = 0', (status,))
            else:
                cursor.execute('UPDATE download_queue SET is_deleted = 1 WHERE is_deleted = 0')
            conn.commit()
            return cursor.rowcount
    
    def get_next_queue_item(self) -> Optional[Dict]:
        """Sıradaki indirme öğesini getir"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM download_queue 
                WHERE status = 'pending' AND is_deleted = 0
                ORDER BY priority DESC, position ASC
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_queue_position(self, queue_id: int, new_position: int) -> bool:
        """Kuyruk öğesinin pozisyonunu güncelle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE download_queue SET position = ? WHERE id = ?', 
                         (new_position, queue_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def reset_stuck_downloads(self) -> int:
        """İndiriliyor durumunda kalmış öğeleri bekliyor durumuna döndür"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE download_queue 
                SET status = 'pending' 
                WHERE status = 'downloading' AND is_deleted = 0
            ''')
            conn.commit()
            return cursor.rowcount
    
    def reorder_queue_positions(self) -> None:
        """Kuyruk pozisyonlarını yeniden düzenle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Tüm aktif öğeleri pozisyona göre sırala
            cursor.execute('''
                SELECT id FROM download_queue 
                WHERE is_deleted = 0 
                ORDER BY position ASC
            ''')
            items = cursor.fetchall()
            
            # Yeni pozisyonları ata
            for idx, (item_id,) in enumerate(items, 1):
                cursor.execute('UPDATE download_queue SET position = ? WHERE id = ?', 
                             (idx, item_id))
            conn.commit()
    
    def is_url_in_queue(self, url: str) -> bool:
        """URL'nin kuyrukta olup olmadığını kontrol et"""
        from utils.youtube_utils import extract_video_id
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Video ID'yi çıkar
            video_id = extract_video_id(url)
            
            if video_id:
                # Video ID ile kontrol et
                cursor.execute('''
                    SELECT COUNT(*) FROM download_queue 
                    WHERE video_id = ? AND is_deleted = 0 AND status != 'completed'
                ''', (video_id,))
            else:
                # Video ID yoksa URL ile kontrol et
                cursor.execute('''
                    SELECT COUNT(*) FROM download_queue 
                    WHERE url = ? AND is_deleted = 0 AND status != 'completed'
                ''', (url,))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def get_queue_duplicates(self) -> List[Dict]:
        """Kuyrukta duplicate URL'leri bul"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, COUNT(*) as count, GROUP_CONCAT(id) as ids
                FROM download_queue 
                WHERE is_deleted = 0
                GROUP BY url 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def remove_queue_duplicates(self) -> int:
        """Kuyruktan duplicate kayıtları temizle (en eskiler kalır)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Her URL için en eski kaydı bul ve diğerlerini sil
            cursor.execute('''
                UPDATE download_queue 
                SET is_deleted = 1 
                WHERE id IN (
                    SELECT id FROM (
                        SELECT id, 
                               ROW_NUMBER() OVER (PARTITION BY url ORDER BY added_at ASC) as rn
                        FROM download_queue 
                        WHERE is_deleted = 0
                    ) t
                    WHERE t.rn > 1
                )
            ''')
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # Pozisyonları yeniden düzenle
            if deleted_count > 0:
                self.reorder_queue_positions()
            
            return deleted_count