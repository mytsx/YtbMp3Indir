#!/usr/bin/env python3
"""Fix placeholder formatting in translation keys that use .format(count)"""

import os
import sqlite3

DB_PATH = 'data/translations.db'


def fix_placeholder_formatting():
    """Update translations to use {count} instead of {}"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False

    updates = [
        {
            'key_text': 'history.messages.deleted',
            'translations': {
                'en': '{count} records deleted.',
                'tr': '{count} kayıt silindi.'
            }
        },
        {
            'key_text': 'history.messages.added_queue',
            'translations': {
                'en': '{count} videos added to queue.',
                'tr': '{count} video kuyruğa eklendi.'
            }
        }
    ]

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            for update in updates:
                key_text = update['key_text']

                # Get key_id
                cursor.execute(
                    'SELECT key_id FROM translation_keys WHERE key_text = ?',
                    (key_text,)
                )
                result = cursor.fetchone()

                if not result:
                    print(f"❌ Key not found: {key_text}")
                    continue

                key_id = result[0]

                # Update translations
                for lang_code, new_text in update['translations'].items():
                    cursor.execute(
                        '''
                        UPDATE translations
                        SET translated_text = ?
                        WHERE key_id = ? AND lang_code = ?
                        ''',
                        (new_text, key_id, lang_code)
                    )

                    print(f"✅ Updated {key_text} ({lang_code}): {new_text}")

            conn.commit()
            print(f"\n✅ Successfully updated {len(updates)} translation keys")
            return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == '__main__':
    fix_placeholder_formatting()
