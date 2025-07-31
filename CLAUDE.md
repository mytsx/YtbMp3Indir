# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube MP3 İndirici is a modern PyQt5-based desktop application for downloading YouTube videos and converting them to MP3 format. The application features a modular architecture with SQLite database persistence, advanced queue management, and comprehensive download history tracking.

## Commands

### Running the Application
```bash
python mp3yap_gui.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Type Checking (Optional)
Type checking is configured via `pyrightconfig.json` but many type issues are suppressed for compatibility.

## Architecture Overview

The application follows a modular PyQt5 architecture organized into distinct packages:

### Core Components

1. **mp3yap_gui.py**: Application entry point with splash screen initialization
   - Handles application lifecycle and module loading
   - Manages startup sequence with animated splash screen
   - Performs database initialization and FFmpeg setup

2. **ui/ package**: User interface components
   - `main_window.py`: Main application window with tabbed interface
   - `splash_screen.py`: Animated startup screen with random color patterns
   - `history_widget.py`: Download history management with statistics
   - `queue_widget.py`: Download queue with priority and position management
   - `settings_dialog.py`: Configuration management interface

3. **core/ package**: Business logic
   - `downloader.py`: YouTube download engine using yt-dlp with FFmpeg integration

4. **database/ package**: Data persistence
   - `manager.py`: SQLite database operations with soft delete support

5. **utils/ package**: Utilities
   - `config.py`: JSON-based configuration management

### Key Architectural Patterns

**Signal/Slot Communication**: Thread-safe communication between downloader and UI using PyQt5's signal system:
- `DownloadSignals` class manages: progress updates, completion notifications, error reporting, status updates

**Thread Management**: Downloads execute in separate threads to maintain UI responsiveness:
- Main thread handles UI updates
- Worker threads handle yt-dlp operations
- Proper cancellation support with cleanup of partial files

**Database Design**: SQLite with soft delete pattern:
- `download_history` table: Complete download records with metadata
- `download_queue` table: Queued downloads with priority/position
- `is_deleted` field enables recovery of "deleted" records
- Automatic database migration support

**Modular UI Architecture**: Tab-based interface with specialized widgets:
- Download tab: URL input, real-time validation, playlist detection
- History tab: Search, statistics, re-download capabilities  
- Queue tab: Priority management, drag-and-drop reordering

## Technical Implementation Details

### Download Engine
- **yt-dlp Integration**: Configurable quality settings (192kbps MP3 default)
- **FFmpeg Handling**: Static FFmpeg auto-installation with system fallback
- **Playlist Support**: Automatic detection with video count preview
- **Duplicate Prevention**: Video ID tracking prevents redundant database entries
- **Progress Tracking**: Real-time progress hooks with cancellation support

### URL Processing Pipeline
1. Regex-based YouTube URL validation
2. Database lookup for existing downloads
3. yt-dlp metadata extraction for playlists
4. Real-time status bar updates with color coding
5. Automatic URL clearing post-download

### Database Operations
- **Soft Delete**: All delete operations use `is_deleted` flag
- **Migration System**: Automatic schema updates via `_add_is_deleted_columns`
- **Query Filtering**: All selects include `is_deleted = 0` condition
- **Statistics**: Real-time calculation of download metrics

### Configuration Management
- JSON-based settings in `config.json`
- Persistent across application restarts
- Controls output directory, auto-open behavior, quality settings

## Development Notes

### Threading Considerations
- UI operations must stay on main thread
- Database operations are thread-safe via connection-per-operation pattern
- Download cancellation requires proper cleanup of yt-dlp instances and partial files

### Error Handling Strategy
- Progress hooks catch cancellation via `is_running` flag
- yt-dlp errors are captured and displayed in status messages
- Database errors are logged but don't crash the application
- FFmpeg availability is checked with graceful degradation

### URL Validation Pipeline
- Regex validation for YouTube URL patterns
- Database exact-match lookup (not partial matching)
- yt-dlp metadata extraction for playlist information
- Debounced input processing (500ms delay) for performance

### File Management
- Downloads saved to configurable `music/` directory
- Automatic cleanup of `.part` and `.ytdl` files on cancellation
- Sanitized filename generation for cross-platform compatibility

## Database Schema

### download_history
- Core fields: `id`, `video_title`, `file_name`, `file_path`, `url`
- Metadata: `format`, `file_size`, `duration`, `channel_name`
- Tracking: `downloaded_at`, `status`, `is_deleted`

### download_queue  
- Management: `id`, `url`, `video_title`, `priority`, `position`
- State: `status`, `added_at`, `started_at`, `completed_at`, `is_deleted`
- Error tracking: `error_message`

## Important Implementation Patterns

When modifying download functionality, always:
1. Update both progress hooks and database save methods
2. Ensure proper thread safety using signals
3. Handle cancellation gracefully with file cleanup
4. Maintain soft delete patterns for data operations
5. Test playlist detection with various YouTube URL formats