#!/usr/bin/env python3
"""Add translation keys for hardcoded strings identified by Gemini Code Assist"""
import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = 'data/translations.db'

# Keys to add - all hardcoded strings identified by Gemini
keys_to_add = [
    # core/downloader.py - 7 locations
    {
        'key_text': 'ffmpeg_load_failed',
        'scope': 'downloader.errors',
        'description': 'Error message when FFmpeg fails to load',
        'translations': {
            'en': 'FFmpeg could not be loaded: {error}',
            'tr': 'FFmpeg yüklenemedi: {error}'
        }
    },
    {
        'key_text': 'saved',
        'scope': 'downloader.status',
        'description': 'Success message when download is saved',
        'translations': {
            'en': '✅ Saved: {title}',
            'tr': '✅ Kaydedildi: {title}'
        }
    },
    {
        'key_text': 'download_cancelled',
        'scope': 'downloader.errors',
        'description': 'Message when download is cancelled',
        'translations': {
            'en': 'Download cancelled',
            'tr': 'İndirme iptal edildi'
        }
    },
    {
        'key_text': 'checking_url',
        'scope': 'downloader.status',
        'description': 'Status message when checking URL',
        'translations': {
            'en': '🔗 Checking link: {url}',
            'tr': '🔗 Bağlantı kontrol ediliyor: {url}'
        }
    },
    {
        'key_text': 'ffmpeg_not_found_fallback',
        'scope': 'downloader.warnings',
        'description': 'Warning when FFmpeg is not found, using fallback',
        'translations': {
            'en': 'Warning: FFmpeg not found. Downloading original file format (conversion will not be performed).',
            'tr': 'Uyarı: FFmpeg bulunamadı. Orijinal dosya formatı indirilecek (dönüştürme yapılamayacak).'
        }
    },
    {
        'key_text': 'processing_url_progress',
        'scope': 'downloader.status',
        'description': 'Progress message when processing multiple URLs',
        'translations': {
            'en': 'Processing URL {current}/{total}',
            'tr': 'URL {current}/{total} işleniyor'
        }
    },
    {
        'key_text': 'cancelling',
        'scope': 'downloader.status',
        'description': 'Status message when cancelling download',
        'translations': {
            'en': 'Cancelling download...',
            'tr': 'İndirme iptal ediliyor...'
        }
    },

    # services/url_analyzer.py - 2 locations
    {
        'key_text': 'checking_urls',
        'scope': 'url_analyzer.status',
        'description': 'Status message when checking URLs',
        'translations': {
            'en': '⏳ Checking URLs...',
            'tr': '⏳ URL\'ler kontrol ediliyor...'
        }
    },
    {
        'key_text': 'fetching_playlist_info',
        'scope': 'url_analyzer.status',
        'description': 'Status message when fetching playlist information',
        'translations': {
            'en': '⏳ Fetching playlist information...',
            'tr': '⏳ Playlist bilgisi alınıyor...'
        }
    },

    # mp3yap_gui.py - 1 location
    {
        'key_text': 'loading_modules',
        'scope': 'app.status',
        'description': 'Splash screen message when loading modules',
        'translations': {
            'en': 'Loading modules...',
            'tr': 'Modüller yükleniyor...'
        }
    }
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for key_data in keys_to_add:
            key_text = key_data['key_text']
            scope = key_data['scope']
            description = key_data['description']
            full_key = f"{scope}.{key_text}"

            # Check if key already exists
            cursor.execute('SELECT key_id FROM translation_keys WHERE key_text = ?',
                          (full_key,))
            result = cursor.fetchone()

            if result:
                key_id = result[0]
                print(f"Key '{full_key}' already exists (key_id={key_id})")
            else:
                # Insert translation key
                cursor.execute('''
                    INSERT INTO translation_keys (scope, key_text, description)
                    VALUES (?, ?, ?)
                ''', (scope, full_key, description))
                key_id = cursor.lastrowid
                print(f"✓ Added key '{full_key}' (key_id={key_id})")

            # Add translations
            for lang_code, text in key_data['translations'].items():
                cursor.execute('''
                    INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text, is_verified)
                    VALUES (?, ?, ?, 1)
                ''', (key_id, lang_code, text))
                print(f"  ✓ Added {lang_code}: {text}")

        conn.commit()
        print(f"\n✅ Successfully added {len(keys_to_add)} translation keys!")
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

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
