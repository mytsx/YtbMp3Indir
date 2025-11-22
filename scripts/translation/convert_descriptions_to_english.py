#!/usr/bin/env python3
"""
Convert all Turkish descriptions to English in translation_keys table
"""

import sqlite3
from pathlib import Path

# English descriptions for all keys
ENGLISH_DESCRIPTIONS = {
    # Common buttons and labels
    "common.buttons.browse": "Browse button for file/folder selection",
    "common.buttons.cancel": "Cancel action button",
    "common.buttons.save": "Save changes button",
    "common.buttons.ok": "OK/Confirm button",
    "common.buttons.close": "Close window button",
    
    # Converter module
    "converter.buttons.cancel": "Cancel conversion process button",
    "converter.buttons.clear_list": "Clear file list button",
    "converter.buttons.select_file": "Open file selection dialog button",
    "converter.buttons.start_conversion": "Start conversion process button",
    "converter.checkboxes.delete_original": "Delete original file after conversion checkbox",
    "converter.description": "Converter tab description text - file selection and drag-drop info",
    "converter.errors.ffmpeg_message": "Detailed error message when FFmpeg is not found",
    "converter.errors.ffmpeg_not_found_convert": "FFmpeg not found error for conversion",
    "converter.errors.ffmpeg_not_found_select": "FFmpeg not found error for file selection",
    "converter.errors.ffmpeg_title": "FFmpeg error dialog title",
    "converter.labels.drag_drop": "Drag and drop area information text",
    "converter.labels.will_be_deleted": "Warning text about original files deletion",
    "converter.title": "Converter tab title",
    "converter.tooltips.delete_original": "Tooltip for delete original file checkbox",
    "converter.warnings.delete_warning": "Important warning about audio files deletion",
    
    # Dialog messages and titles
    "dialogs.messages.language_change_error": "Error message when language change fails",
    "dialogs.titles.error": "General error dialog title",
    "dialogs.titles.select_files": "File selection dialog window title",
    "dialogs.titles.select_folder": "Folder selection dialog window title",
    
    # History module
    "history.buttons.delete_selected": "Delete selected history records button",
    "history.buttons.refresh": "Refresh history list button",
    "history.buttons.start": "Start download from history button",
    "history.columns.downloaded": "Download date/time column header",
    "history.columns.duration": "Video/audio duration column header",
    "history.columns.file_name": "Downloaded file name column header",
    "history.menu.copy_url": "Copy URL to clipboard menu item",
    "history.menu.delete": "Delete from history menu item",
    "history.menu.download_again": "Download again menu item",
    "history.menu.open_location": "Open file location menu item",
    "history.menu.play": "Play file menu item",
    "history.placeholders.search": "Search box placeholder text",
    "history.stats.duration": "Total duration statistics label",
    "history.stats.size": "Total file size statistics label",
    "history.stats.this_week": "This week statistics label",
    "history.stats.total": "Total downloads statistics label",
    "history.title": "History tab title",
    
    # Main window
    "main.buttons.download": "Start YouTube MP3 download button",
    "main.buttons.download_action": "Download tab title and tab label",
    "main.buttons.paste": "Paste URL from clipboard button",
    "main.buttons.clear": "Clear URL input field button",
    "main.buttons.analyze": "Analyze playlist video count button",
    "main.labels.url": "YouTube URL input field label",
    "main.menu.about": "About menu item",
    "main.menu.check_updates": "Check for updates menu item",
    "main.menu.exit": "Exit application menu item",
    "main.menu.export_history": "Export history menu item",
    "main.menu.file": "File menu header",
    "main.menu.help": "Help menu header",
    "main.menu.import_urls": "Import URLs menu item",
    "main.menu.keyboard_shortcuts": "Keyboard shortcuts menu item",
    "main.menu.preferences": "Preferences menu item",
    "main.menu.quit": "Quit application menu item",
    "main.menu.settings": "Open settings window menu item",
    "main.placeholders.youtube_url": "URL input field placeholder text",
    "main.status.already_downloaded": "Video already downloaded warning",
    "main.status.analyzing_playlist": "Analyzing playlist message",
    "main.status.cancelled": "Download cancelled message",
    "main.status.download_complete": "Download completed successfully message",
    "main.status.downloading": "Download in progress message",
    "main.status.enter_url": "URL required warning",
    "main.status.error": "Error status message prefix",
    "main.status.invalid_url": "Invalid YouTube URL warning",
    "main.status.playlist_detected": "Playlist detected message",
    "main.status.ready": "Application ready status message",
    "main.tabs.convert": "Convert tab label",
    "main.tabs.convert_en": "Convert tab label (English)",
    "main.tabs.history": "History tab label",
    "main.tabs.history_en": "History tab label (English)",
    "main.tabs.queue": "Queue tab label",
    "main.tabs.queue_en": "Queue tab label (English)",
    "main.window.title": "Main window title - YouTube MP3 Downloader",
    
    # Queue module
    "queue.buttons.pause": "Pause download button",
    "queue.buttons.pause_all": "Pause all active downloads button",
    "queue.buttons.start": "Start queue processing button",
    "queue.columns.title": "Video title column header",
    "queue.columns.url": "Video URL column header",
    "queue.columns.priority": "Priority column header",
    "queue.columns.status": "Download status column header",
    "queue.columns.progress": "Download progress column header",
    "queue.columns.added": "Added time column header",
    "queue.context.priority_high": "Set high priority menu item",
    "queue.context.priority_low": "Set low priority menu item",
    "queue.context.priority_normal": "Set normal priority menu item",
    "queue.context.remove": "Remove from queue menu item",
    "queue.context.retry": "Retry download menu item",
    "queue.filters.all": "Show all items filter",
    "queue.labels.active_downloads": "Active downloads count label",
    "queue.labels.queued_items": "Queued items count label",
    "queue.labels.search": "Search field label",
    "queue.menu.clear_all": "Clear entire queue menu item",
    "queue.menu.clear_canceled": "Clear cancelled downloads menu item",
    "queue.menu.clear_completed": "Clear completed downloads menu item",
    "queue.menu.clear_failed": "Clear failed downloads menu item",
    "queue.menu.clear_selected": "Clear selected items menu item",
    "queue.placeholders.search": "Queue search box placeholder",
    "queue.status.completed": "Completed status",
    "queue.status.downloading": "Downloading status",
    "queue.status.failed": "Failed status",
    "queue.status.paused": "Paused status",
    "queue.status.waiting": "Waiting status",
    "queue.title": "Download queue tab title",
    
    # Settings dialog
    "settings.checkboxes.auto_open_folder": "Auto-open folder after download checkbox",
    "settings.checkboxes.auto_retry": "Auto-retry failed downloads checkbox",
    "settings.checkboxes.notification_sound": "Play sound on completion checkbox",
    "settings.groups.appearance": "Appearance settings group title",
    "settings.groups.audio_settings": "Audio settings group title",
    "settings.groups.download_location": "Download location group title",
    "settings.groups.notifications": "Notification settings group title",
    "settings.groups.performance": "Performance settings group title",
    "settings.labels.audio_quality": "MP3 audio quality selection label (128/192/320 kbps)",
    "settings.labels.concurrent_downloads": "Maximum simultaneous downloads count",
    "settings.labels.keep_history": "History retention period label",
    "settings.labels.language": "Language selection label",
    "settings.labels.playlist_limit": "Maximum videos from playlist limit",
    "settings.labels.theme": "Theme selection label",
    "settings.labels.url_cache_limit": "Maximum URLs in memory cache",
    "settings.tabs.application": "Application settings tab",
    "settings.tabs.download": "Download settings tab",
    "settings.tooltips.cache_limit": "URL cache limit explanation tooltip",
    "settings.values.history_30_days": "30 days history option",
    "settings.values.history_60_days": "60 days history option",
    "settings.values.history_90_days": "90 days history option",
    "settings.values.history_forever": "Keep history forever option",
    "settings.values.theme_dark": "Dark theme option",
    "settings.values.theme_light": "Light theme option",
    "settings.values.unlimited": "Unlimited value",
    "settings.window.title": "Settings window title",
    
    # Shortcuts
    "shortcuts.categories.download": "Download operations shortcuts category",
    "shortcuts.categories.general": "General shortcuts category",
    "shortcuts.categories.navigation": "Tab navigation shortcuts category",
    "shortcuts.download.clear_url": "Clear URL field shortcut description",
    "shortcuts.download.paste_url": "Paste URL from clipboard shortcut description",
    "shortcuts.download.start_download": "Start download shortcut description",
    "shortcuts.general.about": "Open about dialog shortcut description",
    "shortcuts.general.quit": "Quit application shortcut description",
    "shortcuts.general.settings": "Open settings window shortcut description",
    "shortcuts.navigation.converter_tab": "Switch to converter tab shortcut description",
    "shortcuts.navigation.download_tab": "Switch to download tab shortcut description",
    "shortcuts.navigation.history_tab": "Switch to history tab shortcut description",
    "shortcuts.navigation.queue_tab": "Switch to queue tab shortcut description",
    
    # Splash screen
    "splash.initializing": "Initializing modules message",
    "splash.loading": "Loading application message",
    
    # Status messages
    "status.failed": "Operation failed status indicator",
    "status.loading": "Loading status indicator",
    "status.processing": "Processing status indicator",
    "status.success": "Operation successful status indicator"
}

def convert_to_english():
    """Convert all descriptions to English"""
    db_path = Path('data/translations.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all keys
        cursor.execute("SELECT key_text FROM translation_keys ORDER BY key_text")
        all_keys = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(all_keys)} keys to update")
        
        # Update each key with English description
        updated_count = 0
        for key in all_keys:
            if key in ENGLISH_DESCRIPTIONS:
                description = ENGLISH_DESCRIPTIONS[key]
            else:
                # Generate a basic English description from key structure
                parts = key.split('.')
                if len(parts) >= 2:
                    category = parts[0].title()
                    subcategory = parts[1].replace('_', ' ').title()
                    item = parts[-1].replace('_', ' ')
                    description = f"{category} {subcategory} - {item}"
                else:
                    description = key.replace('.', ' ').replace('_', ' ').title()
            
            cursor.execute("""
                UPDATE translation_keys 
                SET description = ? 
                WHERE key_text = ?
            """, (description, key))
            
            if cursor.rowcount > 0:
                updated_count += 1
        
        conn.commit()
        print(f"Updated {updated_count} descriptions to English")
        
        # Verify the update
        cursor.execute("""
            SELECT key_text, description 
            FROM translation_keys 
            ORDER BY RANDOM()
            LIMIT 10
        """)
        
        print("\nSample updated descriptions:")
        for key, desc in cursor.fetchall():
            print(f"  {key}: {desc}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if convert_to_english():
        print("\n✓ Successfully converted all descriptions to English")
    else:
        print("\n✗ Failed to convert descriptions")