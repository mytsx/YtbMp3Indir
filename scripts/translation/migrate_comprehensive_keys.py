#!/usr/bin/env python3
"""
Comprehensive translation key migration script.
Adds all missing hierarchical translation keys to database.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

DB_PATH = project_root / 'data' / 'translations.db'
MAPPING_FILE = Path(__file__).parent / 'translation_key_mapping_comprehensive.json'


def load_mapping():
    """Load the comprehensive key mapping"""
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_existing_keys(conn):
    """Get all existing translation keys"""
    cursor = conn.cursor()
    cursor.execute("SELECT key_text FROM translation_keys")
    return {row[0] for row in cursor.fetchall()}


def add_translation_key(conn, key_text, description=""):
    """Add a new translation key"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO translation_keys (key_text, description, created_at)
        VALUES (?, ?, datetime('now'))
    """, (key_text, description))
    return cursor.lastrowid


def add_translation(conn, key_id, lang_code, translated_text):
    """Add a translation for a key"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text, updated_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (key_id, lang_code, translated_text))


def migrate_keys():
    """Main migration function"""
    print("=" * 80)
    print("COMPREHENSIVE TRANSLATION KEY MIGRATION")
    print("=" * 80)

    # Load mapping
    print(f"\n📖 Loading mapping from: {MAPPING_FILE}")
    mapping_data = load_mapping()
    translations_tr = mapping_data['translations']['tr']
    translations_en = mapping_data['translations']['en']

    print(f"✓ Found {len(translations_tr)} TR translations")
    print(f"✓ Found {len(translations_en)} EN translations")

    # Connect to database
    print(f"\n💾 Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    try:
        # Get existing keys
        existing_keys = get_existing_keys(conn)
        print(f"✓ Database has {len(existing_keys)} existing keys")

        # Collect all unique keys from translations
        all_new_keys = set(translations_tr.keys()) | set(translations_en.keys())
        keys_to_add = all_new_keys - existing_keys

        print(f"\n🆕 Keys to add: {len(keys_to_add)}")

        if not keys_to_add:
            print("✅ No new keys to add!")
            return

        # Add keys
        added_count = 0
        for key_text in sorted(keys_to_add):
            # Determine description from original hardcoded string
            description = f"Migrated from hardcoded string"

            # Add key
            key_id = add_translation_key(conn, key_text, description)

            # Add Turkish translation if available
            if key_text in translations_tr:
                add_translation(conn, key_id, 'tr', translations_tr[key_text])

            # Add English translation if available
            if key_text in translations_en:
                add_translation(conn, key_id, 'en', translations_en[key_text])

            added_count += 1
            print(f"  ✓ Added: {key_text}")

        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully added {added_count} new keys to database!")

        # Verification
        print("\n🔍 Verifying...")
        new_existing_keys = get_existing_keys(conn)
        print(f"✓ Database now has {len(new_existing_keys)} total keys")
        print(f"✓ Added {len(new_existing_keys) - len(existing_keys)} keys")

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    print("\n" + "=" * 80)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == '__main__':
    migrate_keys()
