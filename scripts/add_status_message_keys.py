#!/usr/bin/env python3
"""Add missing status message translation keys"""
import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = 'data/translations.db'

# Keys to add
keys_to_add = [
    {
        'key_text': 'all_downloads_completed',
        'scope': 'main.status',
        'description': 'Message shown when all downloads are complete',
        'translations': {
            'en': '🎉 All downloads completed!',
            'tr': '🎉 Tüm indirmeler tamamlandı!'
        }
    },
    {
        'key_text': 'download_stopped',
        'scope': 'main.status',
        'description': 'Message shown when download is cancelled/stopped',
        'translations': {
            'en': 'Download stopped',
            'tr': 'İndirme durduruldu'
        }
    },
    {
        'key_text': 'url_added_to_download_tab',
        'scope': 'main.status',
        'description': 'Message shown when URL is added to download tab',
        'translations': {
            'en': '✓ URL added to download tab',
            'tr': '✓ URL indir sekmesine eklendi'
        }
    }
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for key_data in keys_to_add:
        key_text = key_data['key_text']
        scope = key_data['scope']
        description = key_data['description']

        # Check if key already exists
        cursor.execute('SELECT key_id FROM translation_keys WHERE key_text = ? AND scope = ?',
                      (key_text, scope))
        result = cursor.fetchone()

        if result:
            key_id = result[0]
            print(f"Key '{scope}.{key_text}' already exists (key_id={key_id})")
        else:
            # Insert translation key
            cursor.execute('''
                INSERT INTO translation_keys (scope, key_text, description)
                VALUES (?, ?, ?)
            ''', (scope, key_text, description))
            key_id = cursor.lastrowid
            print(f"✓ Added key '{scope}.{key_text}' (key_id={key_id})")

        # Add translations
        for lang_code, text in key_data['translations'].items():
            cursor.execute('''
                INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text, is_verified)
                VALUES (?, ?, ?, 1)
            ''', (key_id, lang_code, text))
            print(f"  ✓ Added {lang_code}: {text}")

    conn.commit()
    conn.close()
    print("\n✅ All status message keys added successfully!")

if __name__ == '__main__':
    main()
