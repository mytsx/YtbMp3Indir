#!/usr/bin/env python3
"""Add all missing downloader translation keys identified in code review"""

import sqlite3
import os

DB_PATH = 'data/translations.db'

def add_downloader_translations():
    """Add comprehensive downloader translation keys"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False

    keys_to_add = [
        # Status Messages
        {
            'key_text': 'downloader.status.playlist_downloading_item',
            'scope': 'downloader.status',
            'description': 'Status message when downloading playlist item',
            'translations': {
                'en': '📥 [{current}/{total}] Downloading playlist...',
                'tr': '📥 [{current}/{total}] Playlist indiriliyor...'
            }
        },
        {
            'key_text': 'downloader.status.error_prefix',
            'scope': 'downloader.status',
            'description': 'Error message prefix',
            'translations': {
                'en': '❌ Error: {msg}',
                'tr': '❌ Hata: {msg}'
            }
        },
        {
            'key_text': 'downloader.status.converting_to_mp3',
            'scope': 'downloader.status',
            'description': 'Converting to MP3 status',
            'translations': {
                'en': '🔄 {prefix}Converting to MP3...',
                'tr': '🔄 {prefix}MP3\'e dönüştürülüyor...'
            }
        },
        {
            'key_text': 'downloader.status.conversion_in_progress',
            'scope': 'downloader.status',
            'description': 'Conversion in progress status',
            'translations': {
                'en': '🔄 {prefix}Conversion in progress...',
                'tr': '🔄 {prefix}Dönüştürme devam ediyor...'
            }
        },
        {
            'key_text': 'downloader.status.conversion_completed',
            'scope': 'downloader.status',
            'description': 'Conversion completed status',
            'translations': {
                'en': '✨ {prefix}Conversion completed!',
                'tr': '✨ {prefix}Dönüştürme tamamlandı!'
            }
        },
        {
            'key_text': 'downloader.status.downloading_percent',
            'scope': 'downloader.status',
            'description': 'Downloading with percentage',
            'translations': {
                'en': '📥 {prefix}Downloading: {filename} - {percent}%',
                'tr': '📥 {prefix}İndiriliyor: {filename} - %{percent}'
            }
        },
        {
            'key_text': 'downloader.status.downloading_mb',
            'scope': 'downloader.status',
            'description': 'Downloading with MB progress',
            'translations': {
                'en': '📥 {prefix}Downloading: {filename} - {mb} MB',
                'tr': '📥 {prefix}İndiriliyor: {filename} - {mb} MB'
            }
        },
        {
            'key_text': 'downloader.status.download_complete_converting',
            'scope': 'downloader.status',
            'description': 'Download complete, now converting',
            'translations': {
                'en': '✅ {prefix}Download complete, converting to MP3...',
                'tr': '✅ {prefix}İndirme tamamlandı, MP3\'e dönüştürülüyor...'
            }
        },
        {
            'key_text': 'downloader.status.playlist_started',
            'scope': 'downloader.status',
            'description': 'Playlist download started',
            'translations': {
                'en': '📋 Playlist started: {title} ({count} videos)',
                'tr': '📋 Playlist başlatıldı: {title} ({count} video)'
            }
        },
        {
            'key_text': 'downloader.status.downloaded_no_ffmpeg',
            'scope': 'downloader.status',
            'description': 'Downloaded but FFmpeg needed',
            'translations': {
                'en': '✅ Downloaded: {title}.{ext} (FFmpeg required for MP3 conversion)',
                'tr': '✅ İndirildi: {title}.{ext} (MP3 dönüşümü için FFmpeg gerekli)'
            }
        },
        {
            'key_text': 'downloader.status.process_completed',
            'scope': 'downloader.status',
            'description': 'Process completed successfully',
            'translations': {
                'en': '✅ Process completed: {title}.mp3',
                'tr': '✅ İşlem tamamlandı: {title}.mp3'
            }
        },
        {
            'key_text': 'downloader.status.download_completed',
            'scope': 'downloader.status',
            'description': 'Download completed',
            'translations': {
                'en': '✅ Download completed',
                'tr': '✅ İndirme tamamlandı'
            }
        },
        # Error Messages
        {
            'key_text': 'downloader.errors.unknown_file',
            'scope': 'downloader.errors',
            'description': 'Unknown file error',
            'translations': {
                'en': 'Unknown file',
                'tr': 'Bilinmeyen dosya'
            }
        },
        {
            'key_text': 'downloader.errors.unknown_error',
            'scope': 'downloader.errors',
            'description': 'Unknown error',
            'translations': {
                'en': 'Unknown error',
                'tr': 'Bilinmeyen hata'
            }
        },
        {
            'key_text': 'downloader.errors.download_error',
            'scope': 'downloader.errors',
            'description': 'Download error with details',
            'translations': {
                'en': 'Download error: {error}',
                'tr': 'İndirme hatası: {error}'
            }
        },
        {
            'key_text': 'downloader.errors.stopped_by_user',
            'scope': 'downloader.errors',
            'description': 'Download stopped by user',
            'translations': {
                'en': 'Download stopped by user',
                'tr': 'İndirme kullanıcı tarafından durduruldu'
            }
        },
        {
            'key_text': 'downloader.errors.filesystem_error',
            'scope': 'downloader.errors',
            'description': 'Filesystem error',
            'translations': {
                'en': 'Filesystem error: {error}',
                'tr': 'Dosya sistem hatası: {error}'
            }
        },
        {
            'key_text': 'downloader.errors.unexpected_error',
            'scope': 'downloader.errors',
            'description': 'Unexpected error',
            'translations': {
                'en': 'Unexpected error: {error}',
                'tr': 'Beklenmeyen hata: {error}'
            }
        },
        # Default Values
        {
            'key_text': 'downloader.default.unnamed_playlist',
            'scope': 'downloader.default',
            'description': 'Default name for unnamed playlist',
            'translations': {
                'en': 'Unnamed Playlist',
                'tr': 'İsimsiz Playlist'
            }
        },
        # Exception identifiers (English only for programmatic use)
        {
            'key_text': 'downloader.exception.download_cancelled_marker',
            'scope': 'downloader.exception',
            'description': 'Constant marker for cancelled downloads (English only)',
            'translations': {
                'en': 'DOWNLOAD_CANCELLED_BY_USER',
                'tr': 'DOWNLOAD_CANCELLED_BY_USER'  # Same in both languages
            }
        }
    ]

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            added = 0
            updated = 0

            for key_data in keys_to_add:
                key_text = key_data['key_text']

                # Check if key exists
                cursor.execute('SELECT key_id FROM translation_keys WHERE key_text = ?', (key_text,))
                result = cursor.fetchone()

                if result:
                    key_id = result[0]
                    print(f"⏭️  Key exists: {key_text}")
                else:
                    # Insert key
                    cursor.execute('''
                        INSERT INTO translation_keys (key_text, scope, description)
                        VALUES (?, ?, ?)
                    ''', (key_text, key_data['scope'], key_data['description']))
                    key_id = cursor.lastrowid
                    added += 1
                    print(f"✅ Added key: {key_text}")

                # Add/update translations
                for lang_code, text in key_data['translations'].items():
                    cursor.execute('''
                        SELECT translation_id FROM translations
                        WHERE key_id = ? AND lang_code = ?
                    ''', (key_id, lang_code))

                    if cursor.fetchone():
                        cursor.execute('''
                            UPDATE translations
                            SET translated_text = ?
                            WHERE key_id = ? AND lang_code = ?
                        ''', (text, key_id, lang_code))
                        updated += 1
                    else:
                        cursor.execute('''
                            INSERT INTO translations (key_id, lang_code, translated_text)
                            VALUES (?, ?, ?)
                        ''', (key_id, lang_code, text))

            conn.commit()
            print(f"\n✅ Successfully processed {len(keys_to_add)} translation keys")
            print(f"   Added: {added} new keys")
            print(f"   Updated: {updated} translations")
            return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    add_downloader_translations()
