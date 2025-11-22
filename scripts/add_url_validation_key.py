#!/usr/bin/env python3
"""
Add missing URL validation translation key
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.translation_db import translation_db

def add_missing_key():
    """Add missing URL validation key to translation database"""

    key_data = {
        'key_text': 'main.url_validation.checking_urls',
        'scope': 'main.url_validation',
        'description': 'Status message when URL validation/analysis is in progress',
        'translations': {
            'en': '⏳ Checking URLs...',
            'tr': '⏳ URL\'ler kontrol ediliyor...'
        }
    }

    print(f"Adding missing URL validation key...")

    key_text = key_data['key_text']

    # Check if key already exists
    if translation_db.has_key(key_text):
        print(f"  ⚠️  Key '{key_text}' already exists, skipping...")
        return

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
            scope=key_data['scope']
        )
        print(f"     └─ {lang_code}: {text}")

    print("\n✅ URL validation key added successfully!")

if __name__ == '__main__':
    add_missing_key()
