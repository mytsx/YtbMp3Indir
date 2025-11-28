#!/usr/bin/env python3
"""
Script to add keyboard shortcut description translation keys to the database.
These keys are for the keyboard shortcuts help dialog in main_window.py
"""

import sqlite3
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.translation_db import translation_db

# Translation keys for keyboard shortcuts
KEYBOARD_SHORTCUTS_TRANSLATIONS = {
    'shortcuts.descriptions.paste_url': {
        'en': 'Paste URL and auto-validate',
        'tr': 'URL yapıştır ve otomatik doğrula',
        'description': 'Keyboard shortcut description: Paste URL from clipboard and validate'
    },
    'shortcuts.descriptions.quick_download': {
        'en': 'Quick download start',
        'tr': 'Hızlı indirme başlat',
        'description': 'Keyboard shortcut description: Start quick download'
    },
    'shortcuts.descriptions.open_folder': {
        'en': 'Open download folder',
        'tr': 'İndirme klasörünü aç',
        'description': 'Keyboard shortcut description: Open the downloads folder'
    },
    'shortcuts.descriptions.history_tab': {
        'en': 'Switch to history tab',
        'tr': 'Geçmiş sekmesine geç',
        'description': 'Keyboard shortcut description: Navigate to history tab'
    },
    'shortcuts.descriptions.queue_tab': {
        'en': 'Switch to queue tab',
        'tr': 'Kuyruk sekmesine geç',
        'description': 'Keyboard shortcut description: Navigate to queue tab'
    },
    'shortcuts.descriptions.show_help': {
        'en': 'Show this help window',
        'tr': 'Bu yardım penceresini göster',
        'description': 'Keyboard shortcut description: Display keyboard shortcuts help dialog'
    },
    'shortcuts.descriptions.cancel_download': {
        'en': 'Cancel download',
        'tr': 'İndirmeyi iptal et',
        'description': 'Keyboard shortcut description: Cancel ongoing download'
    },
    'shortcuts.descriptions.quit_app': {
        'en': 'Quit application',
        'tr': 'Uygulamadan çık',
        'description': 'Keyboard shortcut description: Exit the application'
    },
}

def add_translations():
    """Add translation keys to the database using TranslationDatabase API."""

    added = 0
    updated = 0
    skipped = 0

    # Get database connection to check for existing keys
    conn = sqlite3.connect(translation_db.db_path)
    cursor = conn.cursor()

    for key, values in KEYBOARD_SHORTCUTS_TRANSLATIONS.items():
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
    print(f"   📝 Total processed: {len(KEYBOARD_SHORTCUTS_TRANSLATIONS)}")
    print("="*60)

    return True

if __name__ == '__main__':
    print("🚀 Adding keyboard shortcut description translation keys...\n")
    success = add_translations()
    if success:
        print("\n✅ Keyboard shortcut translation keys successfully added to database!")
    else:
        print("\n❌ Failed to add translation keys!")
        exit(1)
