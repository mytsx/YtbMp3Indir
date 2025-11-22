#!/usr/bin/env python3
"""Fix queue.messages translation keys - add Turkish translations and fix placeholders"""

import sqlite3
import os

DB_PATH = 'data/translations.db'

def fix_queue_messages():
    """Add Turkish translations and fix placeholder formatting for queue.messages keys"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False

    updates = [
        {
            'key_text': 'queue.messages.items_removed',
            'translations': {
                'en': '{count} items removed from queue.',
                'tr': '{count} öğe kuyruktan kaldırıldı.'
            }
        },
        {
            'key_text': 'queue.messages.items_cleared',
            'translations': {
                'en': '{count} items cleared from queue.',
                'tr': '{count} öğe kuyruktan temizlendi.'
            }
        },
        {
            'key_text': 'queue.messages.selected_cleared',
            'translations': {
                'en': '{count} items cleared.',
                'tr': '{count} öğe temizlendi.'
            }
        },
        {
            'key_text': 'queue.messages.completed_cleared',
            'translations': {
                'en': '{count} completed downloads cleared.',
                'tr': '{count} tamamlanan indirme temizlendi.'
            }
        },
        {
            'key_text': 'queue.messages.failed_cleared',
            'translations': {
                'en': '{count} failed downloads cleared.',
                'tr': '{count} başarısız indirme temizlendi.'
            }
        },
        {
            'key_text': 'queue.messages.canceled_cleared',
            'translations': {
                'en': '{count} canceled downloads cleared.',
                'tr': '{count} iptal edilen indirme temizlendi.'
            }
        }
    ]

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            for update in updates:
                key_text = update['key_text']

                # Get key_id
                cursor.execute('SELECT key_id FROM translation_keys WHERE key_text = ?', (key_text,))
                result = cursor.fetchone()

                if not result:
                    print(f"❌ Key not found: {key_text}")
                    continue

                key_id = result[0]

                # Update or insert translations
                for lang_code, new_text in update['translations'].items():
                    # Check if translation exists
                    cursor.execute('''
                        SELECT translation_id FROM translations
                        WHERE key_id = ? AND lang_code = ?
                    ''', (key_id, lang_code))

                    if cursor.fetchone():
                        # Update existing
                        cursor.execute('''
                            UPDATE translations
                            SET translated_text = ?
                            WHERE key_id = ? AND lang_code = ?
                        ''', (new_text, key_id, lang_code))
                        print(f"✅ Updated {key_text} ({lang_code}): {new_text}")
                    else:
                        # Insert new
                        cursor.execute('''
                            INSERT INTO translations (key_id, lang_code, translated_text)
                            VALUES (?, ?, ?)
                        ''', (key_id, lang_code, new_text))
                        print(f"✅ Added {key_text} ({lang_code}): {new_text}")

            conn.commit()
            print(f"\n✅ Successfully processed {len(updates)} translation keys")
            return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    fix_queue_messages()
