#!/usr/bin/env python3
"""
Add missing English translations for keys that only have Turkish.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'translations.db'

# Manual translations for missing EN keys
MISSING_EN_TRANSLATIONS = {
    # Main labels
    "main.labels.completed": "Completed",
    "main.labels.file": "File",
    "main.labels.paste_urls": "Paste URLs",
    "main.labels.total": "Total",
    "main.labels.waiting": "Waiting",
    "main.buttons.add_to_queue": "Add to Queue",

    # Queue menu
    "queue.menu.clear_completed": "Clear Completed",
    "queue.menu.download_now": "Download Now",
    "queue.menu.download_selected": "Download Selected",
    "queue.menu.item": "item",
    "queue.menu.items": "items",
    "queue.menu.priority": "Priority",
    "queue.menu.retry": "Retry",

    # Queue buttons
    "queue.buttons.move_down": "Move Down",
    "queue.buttons.move_up": "Move Up",
    "queue.buttons.remove": "Remove",

    # Queue columns
    "queue.columns.action": "Action",

    # Queue filters/labels/status
    "queue.filters.all": "All",
    "queue.labels.filter": "Filter",
    "queue.labels.search": "Search",
    "queue.placeholders.search": "Search in queue...",
    "queue.priority.high": "High",
    "queue.priority.normal": "Normal",
    "queue.priority.low": "Low",
    "queue.status.converting": "Converting",
    "queue.status.queued": "Queued",

    # History
    "history.buttons.clear": "Clear",
    "history.buttons.refresh": "Refresh",
    "history.columns.actions": "Actions",
    "history.columns.format": "Format",
    "history.menu.add_download": "Add to Download",
    "history.menu.add_queue": "Add to Queue",
    "history.messages.added_queue": "Added to queue",
    "history.messages.deleted": "Deleted",
    "history.placeholders.search": "Search in title or channel name...",
    "history.stats.summary": "Total: {} files | Size: {:.1f} MB | Today: {} files",
    "history.tooltips.clear": "Clear history",
    "history.tooltips.delete": "Delete",
    "history.tooltips.open_browser": "Open in browser",
    "history.tooltips.refresh": "Refresh",
    "history.warnings.no_videos": "No videos found in history to add.",
    "history.warnings.select_download": "Please select videos to add to download tab.",
    "history.warnings.select_queue": "Please select videos to add to queue.",

    # Converter
    "converter.labels.will_be_deleted": "Original file will be deleted after conversion",
    "converter.tooltips.delete_original": "Delete original file after successful conversion",
    "converter.warnings.delete_warning": "Warning: Original files will be deleted!",

    # Dialogs
    "dialogs.titles.select_files": "Select Files",
}


def get_keys_missing_en(conn):
    """Get all keys that have TR but no EN translation"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT k.key_id, k.key_text
        FROM translation_keys k
        WHERE EXISTS (
            SELECT 1 FROM translations t
            WHERE t.key_id = k.key_id AND t.lang_code = 'tr'
        )
        AND NOT EXISTS (
            SELECT 1 FROM translations t
            WHERE t.key_id = k.key_id AND t.lang_code = 'en'
        )
        AND (
            k.key_text LIKE 'main.%'
            OR k.key_text LIKE 'queue.%'
            OR k.key_text LIKE 'dialogs.%'
            OR k.key_text LIKE 'history.%'
            OR k.key_text LIKE 'converter.%'
        )
        ORDER BY k.key_text
    """)
    return cursor.fetchall()


def add_translation(conn, key_id, lang_code, translated_text):
    """Add a translation"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text, updated_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (key_id, lang_code, translated_text))


def main():
    print("=" * 80)
    print("ADDING MISSING ENGLISH TRANSLATIONS")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)

    try:
        # Get keys missing EN translation
        missing = get_keys_missing_en(conn)
        print(f"\n📋 Found {len(missing)} keys missing EN translation")

        added_count = 0
        for key_id, key_text in missing:
            if key_text in MISSING_EN_TRANSLATIONS:
                en_text = MISSING_EN_TRANSLATIONS[key_text]
                add_translation(conn, key_id, 'en', en_text)
                print(f"  ✓ Added: {key_text} = {en_text}")
                added_count += 1
            else:
                print(f"  ⚠️  Skipped (no translation provided): {key_text}")

        conn.commit()
        print(f"\n✅ Successfully added {added_count} English translations!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    print("=" * 80)


if __name__ == '__main__':
    main()
