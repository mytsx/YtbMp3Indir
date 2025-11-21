#!/usr/bin/env python3
"""Add final remaining EN translations"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'translations.db'

# Final translations
TRANSLATIONS = {
    # Old-style keys (deprecated but still used)
    "buttons.add_to_queue": "Add to Queue",
    "common.status.loading": "Loading...",
    "labels.completed": "Completed",
    "labels.file": "File",
    "labels.filter": "Filter",
    "labels.paste_urls": "Paste URLs",
    "labels.search": "Search",
    "labels.total": "Total",
    "labels.waiting": "Waiting",
    "menu.clear_canceled": "Clear Cancelled",
    "menu.clear_failed": "Clear Failed",
    "menu.clear_selected": "Clear Selected",
    "placeholders.search": "Search...",

    # Plain text (already in English)
    "Cancelling...": "Cancelling...",
    "Convert your video, audio and other media files to MP3 format. You can drag and drop files or select them.": "Convert your video, audio and other media files to MP3 format. You can drag and drop files or select them.",
    "Error ({}): File could not be converted. Please check that the file is not corrupted and is in a supported format.": "Error ({}): File could not be converted. Please check that the file is not corrupted and is in a supported format.",
    "FFmpeg is required for conversion feature. Please install FFmpeg or restart the application.": "FFmpeg is required for conversion feature. Please install FFmpeg or restart the application.",
    "Loading...": "Loading...",
    "No videos found in history to add.": "No videos found in history to add.",
    "Please select videos to add to download tab.": "Please select videos to add to download tab.",
    "Please select videos to add to queue.": "Please select videos to add to queue.",
    "Search in title or channel name...": "Search in title or channel name...",
    "Total: {} files | Size: {:.1f} MB | Today: {} files": "Total: {} files | Size: {:.1f} MB | Today: {} files",
    "{} records deleted.": "{} records deleted.",
    "{} videos added to queue.": "{} videos added to queue.",
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added = 0
    for key_text, en_text in TRANSLATIONS.items():
        # Get key_id
        cursor.execute("SELECT key_id FROM translation_keys WHERE key_text = ?", (key_text,))
        result = cursor.fetchone()

        if result:
            key_id = result[0]
            # Add EN translation
            cursor.execute("""
                INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text, updated_at)
                VALUES (?, 'en', ?, datetime('now'))
            """, (key_id, en_text))
            print(f"✓ {key_text}")
            added += 1
        else:
            print(f"⚠️  Key not found: {key_text}")

    conn.commit()
    conn.close()
    print(f"\n✅ Added {added} EN translations!")

if __name__ == '__main__':
    main()
