#!/usr/bin/env python3
"""
Script to add remaining HIGH priority translation keys to the database.
"""

import sqlite3
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from database.translation_db import translation_db

# Translation keys to add
TRANSLATIONS = {
    # ui/main_window.py keys
    'dialogs.errors.file_encoding_error': {
        'en': 'File encoding error: {error}',
        'tr': 'Dosya kodlama hatası: {error}',
        'description': 'Error message shown when file encoding fails'
    },
    'main.url_validation.videos_ready': {
        'en': '✓ {count} videos ready to download',
        'tr': '✓ {count} video indirmeye hazır',
        'description': 'Status message showing number of videos ready to download'
    },
    'main.url_validation.playlists': {
        'en': '{count} playlists',
        'tr': '{count} playlist',
        'description': 'Label showing number of playlists in validation result'
    },
    'main.url_validation.videos': {
        'en': '{count} videos',
        'tr': '{count} video',
        'description': 'Label showing number of videos in validation result'
    },
    'main.url_validation.playlist_item': {
        'en': '  • {title}',
        'tr': '  • {title}',
        'description': 'Bullet point format for playlist item titles'
    },
    'main.url_validation.invalid_urls': {
        'en': '✗ {count} invalid URLs',
        'tr': '✗ {count} geçersiz URL',
        'description': 'Status message showing number of invalid URLs'
    },
    'main.url_validation.files_exist': {
        'en': '✓ {count} files already downloaded and present in folder',
        'tr': '✓ {count} dosya hem indirilmiş hem de klasörde mevcut',
        'description': 'Status message for files that exist both in DB and folder'
    },
    'main.url_validation.files_missing': {
        'en': '⚠ {count} files previously downloaded but not found in folder',
        'tr': '⚠ {count} dosya daha önce indirilmiş ama klasörde bulunamadı',
        'description': 'Warning message for files in DB but missing from folder'
    },
    'main.url_validation.unknown_records': {
        'en': '? {count} records contain incomplete information',
        'tr': '? {count} dosya kaydı eksik bilgi içeriyor',
        'description': 'Warning message for database records with incomplete info'
    },
    # Status detection keywords (for programmatic use)
    'keywords.converting_to_mp3': {
        'en': 'Converting to MP3',
        'tr': 'MP3\'e dönüştürülüyor',
        'description': 'Keyword used to detect MP3 conversion status in progress messages'
    },
    'keywords.conversion': {
        'en': 'Conversion',
        'tr': 'Dönüştürme',
        'description': 'Keyword used to detect conversion status in progress messages'
    },
    # utils/update_checker.py keys
    'update.messages.new_version_available': {
        'en': 'New version available: v{version}',
        'tr': 'Yeni sürüm mevcut: v{version}',
        'description': 'Message shown when a new version is available for update'
    },
    'update.messages.up_to_date': {
        'en': 'You are using the latest version',
        'tr': 'Güncel sürümü kullanıyorsunuz',
        'description': 'Message shown when application is up to date'
    },
    'update.errors.api_response_failed': {
        'en': 'Error: Could not read API response: {error}',
        'tr': 'Hata: API yanıtı okunamadı: {error}',
        'description': 'Error message when GitHub API response cannot be read'
    },
    'update.errors.check_failed': {
        'en': 'Update check failed: {error}',
        'tr': 'Güncelleme kontrolü başarısız: {error}',
        'description': 'Error message when update check fails'
    },
    'update.errors.unexpected_error': {
        'en': 'Error: An unexpected error occurred.',
        'tr': 'Hata: Beklenmedik bir hata oluştu.',
        'description': 'Generic error message for unexpected errors during update check'
    }
}

def add_translations():
    """Add translation keys to the database using TranslationDatabase API."""

    added = 0
    updated = 0
    skipped = 0

    # Get database connection to check for existing keys
    conn = sqlite3.connect(translation_db.db_path)
    cursor = conn.cursor()

    for key, values in TRANSLATIONS.items():
        # Check if key already exists
        cursor.execute("""
            SELECT k.key_id, t_en.translated_text as en, t_tr.translated_text as tr
            FROM translation_keys k
            LEFT JOIN translations t_en ON k.key_id = t_en.key_id AND t_en.lang_code = 'en'
            LEFT JOIN translations t_tr ON k.key_id = t_tr.key_id AND t_tr.lang_code = 'tr'
            WHERE k.key_text = ?
        """, (key,))

        existing = cursor.fetchone()

        if existing:
            key_id, existing_en, existing_tr = existing
            # Check if values are different
            if existing_en != values['en'] or existing_tr != values['tr']:
                # Update using the API
                translation_db.add_translation(key, 'en', values['en'])
                translation_db.add_translation(key, 'tr', values['tr'])

                # Update description
                cursor.execute("""
                    UPDATE translation_keys
                    SET description = ?
                    WHERE key_id = ?
                """, (values['description'], key_id))
                conn.commit()

                print(f"✏️  Updated: {key}")
                updated += 1
            else:
                print(f"⏭️  Skipped (identical): {key}")
                skipped += 1
        else:
            # Add new translation using the API
            translation_db.add_translation(key, 'en', values['en'])
            translation_db.add_translation(key, 'tr', values['tr'])

            # Update description
            cursor.execute("""
                UPDATE translation_keys
                SET description = ?
                WHERE key_text = ?
            """, (values['description'], key))
            conn.commit()

            print(f"✅ Added: {key}")
            added += 1

    conn.close()

    # Clear cache to ensure fresh data
    translation_db.clear_cache()

    print("\n" + "="*60)
    print(f"📊 Summary:")
    print(f"   ✅ Added: {added}")
    print(f"   ✏️  Updated: {updated}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   📝 Total processed: {len(TRANSLATIONS)}")
    print("="*60)

    return True

if __name__ == '__main__':
    print("🚀 Adding remaining HIGH priority translation keys...\n")
    success = add_translations()
    if success:
        print("\n✅ Translation keys successfully added to database!")
    else:
        print("\n❌ Failed to add translation keys!")
        exit(1)
