#!/usr/bin/env python3
"""
Create a clean translations database with proper structure
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def create_clean_database():
    """Create a new clean translations database"""
    
    # Ensure data directory exists
    Path('data').mkdir(exist_ok=True)
    
    # Create new database
    db_path = Path('data/translations.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create languages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS languages (
                lang_code TEXT PRIMARY KEY,
                lang_name TEXT NOT NULL,
                native_name TEXT NOT NULL,
                is_rtl INTEGER DEFAULT 0,
                fallback_lang TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create translation_keys table with English descriptions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translation_keys (
                key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT,
                key_text TEXT NOT NULL UNIQUE,
                description TEXT,
                default_text TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create translations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                translation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id INTEGER NOT NULL,
                lang_code TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                translator_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (key_id) REFERENCES translation_keys(key_id),
                FOREIGN KEY (lang_code) REFERENCES languages(lang_code),
                UNIQUE(key_id, lang_code)
            )
        """)
        
        # Add indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translations_key_lang ON translations(key_id, lang_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_translation_keys_text ON translation_keys(key_text)")
        
        # Insert languages
        languages = [
            ('tr', 'Turkish', 'Türkçe', 0, None, 1),
            ('en', 'English', 'English', 0, None, 1)
        ]
        
        cursor.executemany("""
            INSERT INTO languages (lang_code, lang_name, native_name, is_rtl, fallback_lang, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, languages)
        
        # Translation keys with English descriptions and default texts
        translation_keys = [
            # Main window
            ('main.window.title', 'Main application window title', 'YouTube MP3 Downloader'),
            ('main.buttons.download', 'Download button to start YouTube MP3 download', 'Download'),
            ('main.buttons.download_action', 'Download tab label', 'Download'),
            ('main.buttons.paste', 'Paste URL from clipboard button', 'Paste'),
            ('main.buttons.clear', 'Clear URL input field button', 'Clear'),
            ('main.buttons.analyze', 'Analyze playlist for video count button', 'Analyze'),
            ('main.labels.url', 'URL input field label', 'URL:'),
            ('main.placeholders.youtube_url', 'URL input field placeholder text', 'Enter YouTube URL...'),
            ('main.status.ready', 'Application ready status message', 'Ready'),
            ('main.status.downloading', 'Download in progress status', 'Downloading...'),
            ('main.status.download_complete', 'Download completed message', 'Download Complete'),
            ('main.status.error', 'Error status prefix', 'Error'),
            ('main.status.cancelled', 'Download cancelled message', 'Cancelled'),
            ('main.status.already_downloaded', 'Video already downloaded warning', 'Already Downloaded'),
            ('main.status.playlist_detected', 'Playlist URL detected message', 'Playlist Detected'),
            ('main.status.analyzing_playlist', 'Analyzing playlist message', 'Analyzing Playlist...'),
            ('main.status.invalid_url', 'Invalid URL warning', 'Invalid URL'),
            ('main.status.enter_url', 'URL required warning', 'Please Enter URL'),
            
            # Main menu
            ('main.menu.file', 'File menu header', 'File'),
            ('main.menu.settings', 'Settings menu item', 'Settings'),
            ('main.menu.exit', 'Exit application menu item', 'Exit'),
            ('main.menu.help', 'Help menu header', 'Help'),
            ('main.menu.about', 'About dialog menu item', 'About'),
            ('main.menu.keyboard_shortcuts', 'Keyboard shortcuts menu item', 'Keyboard Shortcuts'),
            
            # Tabs
            ('main.tabs.history', 'History tab label', 'History'),
            ('main.tabs.queue', 'Queue tab label', 'Queue'),
            ('main.tabs.convert', 'Convert tab label', 'Convert'),
            
            # History widget
            ('history.title', 'History tab title', 'Download History'),
            ('history.labels.search', 'Search box placeholder', 'Search...'),
            ('history.labels.total_downloads', 'Total downloads count label', 'Total Downloads'),
            ('history.labels.total_size', 'Total file size label', 'Total Size'),
            ('history.labels.total_duration', 'Total duration label', 'Total Duration'),
            ('history.buttons.clear_history', 'Clear all history button', 'Clear History'),
            ('history.buttons.open_folder', 'Open file location button', 'Open Folder'),
            ('history.buttons.play', 'Play file button', 'Play'),
            ('history.buttons.redownload', 'Download again button', 'Re-download'),
            ('history.buttons.delete', 'Delete from history button', 'Delete'),
            ('history.columns.title', 'Video title column header', 'Title'),
            ('history.columns.channel', 'Channel name column header', 'Channel'),
            ('history.columns.duration', 'Duration column header', 'Duration'),
            ('history.columns.size', 'File size column header', 'Size'),
            ('history.columns.date', 'Download date column header', 'Date'),
            ('history.columns.status', 'Status column header', 'Status'),
            
            # Queue widget
            ('queue.title', 'Queue tab title', 'Download Queue'),
            ('queue.labels.queued_items', 'Queued items count label', 'Queued Items'),
            ('queue.labels.active_downloads', 'Active downloads count label', 'Active Downloads'),
            ('queue.buttons.pause_all', 'Pause all downloads button', 'Pause All'),
            ('queue.buttons.resume_all', 'Resume all downloads button', 'Resume All'),
            ('queue.buttons.clear_completed', 'Clear completed downloads button', 'Clear Completed'),
            ('queue.buttons.clear_all', 'Clear entire queue button', 'Clear All'),
            ('queue.columns.title', 'Video title column', 'Title'),
            ('queue.columns.url', 'URL column', 'URL'),
            ('queue.columns.priority', 'Priority column', 'Priority'),
            ('queue.columns.status', 'Status column', 'Status'),
            ('queue.columns.progress', 'Progress column', 'Progress'),
            ('queue.columns.added', 'Added time column', 'Added'),
            ('queue.status.waiting', 'Waiting status', 'Waiting'),
            ('queue.status.downloading', 'Downloading status', 'Downloading'),
            ('queue.status.completed', 'Completed status', 'Completed'),
            ('queue.status.failed', 'Failed status', 'Failed'),
            ('queue.status.paused', 'Paused status', 'Paused'),
            ('queue.context.remove', 'Remove from queue menu item', 'Remove'),
            ('queue.context.retry', 'Retry download menu item', 'Retry'),
            ('queue.context.priority_high', 'Set high priority menu item', 'High Priority'),
            ('queue.context.priority_normal', 'Set normal priority menu item', 'Normal Priority'),
            ('queue.context.priority_low', 'Set low priority menu item', 'Low Priority'),
            
            # Converter widget
            ('converter.title', 'Converter tab title', 'File Converter'),
            ('converter.description', 'Converter description text', 'Convert media files to MP3'),
            ('converter.buttons.select_file', 'Select files button', 'Select Files'),
            ('converter.buttons.start_conversion', 'Start conversion button', 'Start Conversion'),
            ('converter.buttons.cancel', 'Cancel conversion button', 'Cancel'),
            ('converter.buttons.clear_list', 'Clear file list button', 'Clear List'),
            ('converter.checkboxes.delete_original', 'Delete original files checkbox', 'Delete original files'),
            ('converter.labels.drag_drop', 'Drag and drop area text', 'Drag files here'),
            ('converter.errors.ffmpeg_not_found', 'FFmpeg not found error', 'FFmpeg not found'),
            
            # Settings dialog
            ('settings.window.title', 'Settings window title', 'Settings'),
            ('settings.tabs.download', 'Download settings tab', 'Download'),
            ('settings.tabs.application', 'Application settings tab', 'Application'),
            ('settings.groups.audio_settings', 'Audio settings group', 'Audio Settings'),
            ('settings.groups.download_location', 'Download location group', 'Download Location'),
            ('settings.groups.performance', 'Performance settings group', 'Performance'),
            ('settings.groups.appearance', 'Appearance settings group', 'Appearance'),
            ('settings.groups.notifications', 'Notification settings group', 'Notifications'),
            ('settings.labels.audio_quality', 'Audio quality label', 'Audio Quality'),
            ('settings.labels.concurrent_downloads', 'Concurrent downloads label', 'Concurrent Downloads'),
            ('settings.labels.playlist_limit', 'Playlist limit label', 'Playlist Limit'),
            ('settings.labels.url_cache_limit', 'URL cache limit label', 'URL Cache Limit'),
            ('settings.labels.theme', 'Theme selection label', 'Theme'),
            ('settings.labels.language', 'Language selection label', 'Language'),
            ('settings.labels.keep_history', 'History retention label', 'Keep History'),
            ('settings.checkboxes.auto_retry', 'Auto retry failed downloads', 'Auto Retry'),
            ('settings.checkboxes.notification_sound', 'Play completion sound', 'Notification Sound'),
            ('settings.checkboxes.auto_open_folder', 'Auto open folder after download', 'Auto Open Folder'),
            ('settings.values.unlimited', 'Unlimited value option', 'Unlimited'),
            ('settings.values.theme_light', 'Light theme option', 'Light'),
            ('settings.values.theme_dark', 'Dark theme option', 'Dark'),
            ('settings.values.history_30_days', '30 days history option', '30 Days'),
            ('settings.values.history_60_days', '60 days history option', '60 Days'),
            ('settings.values.history_90_days', '90 days history option', '90 Days'),
            ('settings.values.history_forever', 'Keep history forever option', 'Forever'),
            
            # Common buttons
            ('common.buttons.save', 'Save button', 'Save'),
            ('common.buttons.cancel', 'Cancel button', 'Cancel'),
            ('common.buttons.ok', 'OK button', 'OK'),
            ('common.buttons.close', 'Close button', 'Close'),
            ('common.buttons.browse', 'Browse button', 'Browse'),
            
            # Dialogs
            ('dialogs.titles.confirm', 'Confirmation dialog title', 'Confirm'),
            ('dialogs.titles.error', 'Error dialog title', 'Error'),
            ('dialogs.titles.warning', 'Warning dialog title', 'Warning'),
            ('dialogs.titles.info', 'Info dialog title', 'Information'),
            ('dialogs.titles.select_folder', 'Folder selection dialog title', 'Select Folder'),
            ('dialogs.messages.clear_history_confirm', 'Clear history confirmation message', 'Clear all history?'),
            ('dialogs.messages.clear_queue_confirm', 'Clear queue confirmation message', 'Clear all queue?'),
            ('dialogs.messages.delete_confirm', 'Delete confirmation message', 'Delete selected items?'),
            ('dialogs.messages.exit_confirm', 'Exit confirmation with active downloads', 'Downloads in progress. Exit?'),
            
            # Status messages
            ('status.loading', 'Loading status', 'Loading...'),
            ('status.processing', 'Processing status', 'Processing...'),
            ('status.success', 'Success status', 'Success'),
            ('status.failed', 'Failed status', 'Failed')
        ]
        
        # Insert translation keys
        for key_text, description, default_text in translation_keys:
            cursor.execute("""
                INSERT INTO translation_keys (key_text, description, default_text)
                VALUES (?, ?, ?)
            """, (key_text, description, default_text))
        
        # Add Turkish translations
        turkish_translations = {
            'main.window.title': 'YouTube MP3 İndirici',
            'main.buttons.download': 'İndir',
            'main.buttons.download_action': 'İndir',
            'main.buttons.paste': 'Yapıştır',
            'main.buttons.clear': 'Temizle',
            'main.buttons.analyze': 'Analiz Et',
            'main.labels.url': 'URL:',
            'main.placeholders.youtube_url': 'YouTube URL\'sini girin...',
            'main.status.ready': 'Hazır',
            'main.status.downloading': 'İndiriliyor...',
            'main.status.download_complete': 'İndirme Tamamlandı',
            'main.status.error': 'Hata',
            'main.status.cancelled': 'İptal Edildi',
            'main.status.already_downloaded': 'Zaten İndirilmiş',
            'main.status.playlist_detected': 'Oynatma Listesi Algılandı',
            'main.status.analyzing_playlist': 'Oynatma Listesi Analiz Ediliyor...',
            'main.status.invalid_url': 'Geçersiz URL',
            'main.status.enter_url': 'Lütfen URL Girin',
            'main.menu.file': 'Dosya',
            'main.menu.settings': 'Ayarlar',
            'main.menu.exit': 'Çıkış',
            'main.menu.help': 'Yardım',
            'main.menu.about': 'Hakkında',
            'main.menu.keyboard_shortcuts': 'Klavye Kısayolları',
            'main.tabs.history': 'Geçmiş',
            'main.tabs.queue': 'Kuyruk',
            'main.tabs.convert': 'Dönüştür',
            'history.title': 'İndirme Geçmişi',
            'history.labels.search': 'Ara...',
            'history.labels.total_downloads': 'Toplam İndirme',
            'history.labels.total_size': 'Toplam Boyut',
            'history.labels.total_duration': 'Toplam Süre',
            'history.buttons.clear_history': 'Geçmişi Temizle',
            'history.buttons.open_folder': 'Klasörü Aç',
            'history.buttons.play': 'Oynat',
            'history.buttons.redownload': 'Tekrar İndir',
            'history.buttons.delete': 'Sil',
            'history.columns.title': 'Başlık',
            'history.columns.channel': 'Kanal',
            'history.columns.duration': 'Süre',
            'history.columns.size': 'Boyut',
            'history.columns.date': 'Tarih',
            'history.columns.status': 'Durum',
            'queue.title': 'İndirme Kuyruğu',
            'queue.labels.queued_items': 'Kuyruktaki Öğeler',
            'queue.labels.active_downloads': 'Aktif İndirmeler',
            'queue.buttons.pause_all': 'Tümünü Duraklat',
            'queue.buttons.resume_all': 'Tümünü Devam Ettir',
            'queue.buttons.clear_completed': 'Tamamlananları Temizle',
            'queue.buttons.clear_all': 'Tümünü Temizle',
            'queue.columns.title': 'Başlık',
            'queue.columns.url': 'URL',
            'queue.columns.priority': 'Öncelik',
            'queue.columns.status': 'Durum',
            'queue.columns.progress': 'İlerleme',
            'queue.columns.added': 'Eklenme',
            'queue.status.waiting': 'Bekliyor',
            'queue.status.downloading': 'İndiriliyor',
            'queue.status.completed': 'Tamamlandı',
            'queue.status.failed': 'Başarısız',
            'queue.status.paused': 'Duraklatıldı',
            'queue.context.remove': 'Kaldır',
            'queue.context.retry': 'Tekrar Dene',
            'queue.context.priority_high': 'Yüksek Öncelik',
            'queue.context.priority_normal': 'Normal Öncelik',
            'queue.context.priority_low': 'Düşük Öncelik',
            'converter.title': 'Dosya Dönüştürücü',
            'converter.description': 'Medya dosyalarını MP3\'e dönüştür',
            'converter.buttons.select_file': 'Dosya Seç',
            'converter.buttons.start_conversion': 'Dönüştürmeyi Başlat',
            'converter.buttons.cancel': 'İptal',
            'converter.buttons.clear_list': 'Listeyi Temizle',
            'converter.checkboxes.delete_original': 'Orijinal dosyaları sil',
            'converter.labels.drag_drop': 'Dosyaları buraya sürükleyin',
            'converter.errors.ffmpeg_not_found': 'FFmpeg bulunamadı',
            'settings.window.title': 'Ayarlar',
            'settings.tabs.download': 'İndirme',
            'settings.tabs.application': 'Uygulama',
            'settings.groups.audio_settings': 'Ses Ayarları',
            'settings.groups.download_location': 'İndirme Konumu',
            'settings.groups.performance': 'Performans',
            'settings.groups.appearance': 'Görünüm',
            'settings.groups.notifications': 'Bildirimler',
            'settings.labels.audio_quality': 'Ses Kalitesi',
            'settings.labels.concurrent_downloads': 'Eşzamanlı İndirme',
            'settings.labels.playlist_limit': 'Oynatma Listesi Limiti',
            'settings.labels.url_cache_limit': 'URL Önbellek Limiti',
            'settings.labels.theme': 'Tema',
            'settings.labels.language': 'Dil',
            'settings.labels.keep_history': 'Geçmiş Saklama',
            'settings.checkboxes.auto_retry': 'Otomatik Tekrar Dene',
            'settings.checkboxes.notification_sound': 'Bildirim Sesi',
            'settings.checkboxes.auto_open_folder': 'Klasörü Otomatik Aç',
            'settings.values.unlimited': 'Sınırsız',
            'settings.values.theme_light': 'Açık',
            'settings.values.theme_dark': 'Koyu',
            'settings.values.history_30_days': '30 Gün',
            'settings.values.history_60_days': '60 Gün',
            'settings.values.history_90_days': '90 Gün',
            'settings.values.history_forever': 'Süresiz',
            'common.buttons.save': 'Kaydet',
            'common.buttons.cancel': 'İptal',
            'common.buttons.ok': 'Tamam',
            'common.buttons.close': 'Kapat',
            'common.buttons.browse': 'Gözat',
            'dialogs.titles.confirm': 'Onay',
            'dialogs.titles.error': 'Hata',
            'dialogs.titles.warning': 'Uyarı',
            'dialogs.titles.info': 'Bilgi',
            'dialogs.titles.select_folder': 'Klasör Seç',
            'dialogs.messages.clear_history_confirm': 'Tüm geçmiş silinsin mi?',
            'dialogs.messages.clear_queue_confirm': 'Tüm kuyruk temizlensin mi?',
            'dialogs.messages.delete_confirm': 'Seçili öğeler silinsin mi?',
            'dialogs.messages.exit_confirm': 'İndirmeler devam ediyor. Çıkılsın mı?',
            'status.loading': 'Yükleniyor...',
            'status.processing': 'İşleniyor...',
            'status.success': 'Başarılı',
            'status.failed': 'Başarısız'
        }
        
        # Insert Turkish translations
        for key_text, translated_text in turkish_translations.items():
            cursor.execute("""
                INSERT INTO translations (key_id, lang_code, translated_text)
                SELECT key_id, 'tr', ?
                FROM translation_keys
                WHERE key_text = ?
            """, (translated_text, key_text))
        
        # For English, use default_text as translation
        cursor.execute("""
            INSERT INTO translations (key_id, lang_code, translated_text)
            SELECT key_id, 'en', default_text
            FROM translation_keys
        """)
        
        conn.commit()
        print("✓ Created clean translations database")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM translation_keys")
        key_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM translations WHERE lang_code = 'tr'")
        tr_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM translations WHERE lang_code = 'en'")
        en_count = cursor.fetchone()[0]
        
        print(f"\nDatabase Statistics:")
        print(f"  Translation keys: {key_count}")
        print(f"  Turkish translations: {tr_count}")
        print(f"  English translations: {en_count}")
        
        # Show sample data
        print("\nSample translation keys:")
        cursor.execute("""
            SELECT key_text, description, default_text
            FROM translation_keys
            ORDER BY key_text
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}")
            print(f"    Description: {row[1]}")
            print(f"    Default: {row[2]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if create_clean_database():
        print("\n✓ Successfully created clean translations database")
    else:
        print("\n✗ Failed to create database")