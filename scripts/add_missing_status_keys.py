#!/usr/bin/env python3
"""
Add missing status translation keys for download completion messages
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.translation_db import translation_db

def add_missing_keys():
    """Add missing status keys to translation database"""

    keys_to_add = [
        {
            'key_text': 'main.status.all_downloads_completed',
            'scope': 'main.status',
            'description': 'Status message when all downloads (single/playlist/multi-URL) complete successfully',
            'translations': {
                'en': 'All downloads completed',
                'tr': 'Tüm indirmeler tamamlandı'
            }
        },
        {
            'key_text': 'main.status.download_stopped',
            'scope': 'main.status',
            'description': 'Status message when download is stopped/cancelled by user during processing',
            'translations': {
                'en': 'Download stopped',
                'tr': 'İndirme durduruldu'
            }
        }
    ]

    print(f"Adding {len(keys_to_add)} missing status keys...")

    for key_data in keys_to_add:
        key_text = key_data['key_text']

        # Check if key already exists
        if translation_db.has_key(key_text):
            print(f"  ⚠️  Key '{key_text}' already exists, skipping...")
            continue

        # Add the key
        translation_db.add_translation_key(
            key=key_text,
            scope=key_data['scope'],
            description=key_data['description']
        )
        print(f"  ✅ Added key: {key_text}")

        # Add translations
        for lang_code, text in key_data['translations'].items():
            translation_db.add_translation(
                key=key_text,
                lang_code=lang_code,
                text=text,
                scope=key_data['scope']  # ✅ CRITICAL: Must match scope used in add_translation_key
            )
            print(f"     └─ {lang_code}: {text}")

    print("\n✅ All missing status keys added successfully!")

if __name__ == '__main__':
    add_missing_keys()
