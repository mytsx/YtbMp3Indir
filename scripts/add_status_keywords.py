#!/usr/bin/env python3
"""Add translation keys for STATUS_KEYWORDS"""

import sqlite3
import os

DB_PATH = 'data/translations.db'

def add_status_keywords():
    """Add translation keys for status detection keywords"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False

    keys_to_add = [
        {
            'key_text': 'keywords.queued',
            'scope': 'keywords',
            'description': 'Keyword for detecting queued status in messages',
            'translations': {
                'en': 'queued',
                'tr': 'kuyrukta'
            }
        },
        {
            'key_text': 'keywords.added',
            'scope': 'keywords',
            'description': 'Keyword for detecting added status in messages',
            'translations': {
                'en': 'added',
                'tr': 'eklendi'
            }
        },
        {
            'key_text': 'keywords.failed_to_add',
            'scope': 'keywords',
            'description': 'Keyword for detecting failed to add status in messages',
            'translations': {
                'en': 'failed to add',
                'tr': 'eklenemedi'
            }
        }
    ]

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            for key_data in keys_to_add:
                key_text = key_data['key_text']

                # Check if key already exists
                cursor.execute('SELECT key_id FROM translation_keys WHERE key_text = ?', (key_text,))
                existing = cursor.fetchone()

                if existing:
                    print(f"⏭️  Key already exists: {key_text}")
                    key_id = existing[0]
                else:
                    # Insert translation key
                    cursor.execute('''
                        INSERT INTO translation_keys (key_text, scope, description)
                        VALUES (?, ?, ?)
                    ''', (key_text, key_data['scope'], key_data['description']))
                    key_id = cursor.lastrowid
                    print(f"✅ Added key: {key_text}")

                # Add translations
                for lang_code, text in key_data['translations'].items():
                    # Check if translation exists
                    cursor.execute('''
                        SELECT translation_id FROM translations
                        WHERE key_id = ? AND lang_code = ?
                    ''', (key_id, lang_code))

                    if cursor.fetchone():
                        # Update
                        cursor.execute('''
                            UPDATE translations
                            SET translated_text = ?
                            WHERE key_id = ? AND lang_code = ?
                        ''', (text, key_id, lang_code))
                        print(f"   Updated translation ({lang_code}): {text}")
                    else:
                        # Insert
                        cursor.execute('''
                            INSERT INTO translations (key_id, lang_code, translated_text)
                            VALUES (?, ?, ?)
                        ''', (key_id, lang_code, text))
                        print(f"   Added translation ({lang_code}): {text}")

            conn.commit()
            print(f"\n✅ Successfully processed {len(keys_to_add)} keyword translation keys")
            return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    add_status_keywords()
