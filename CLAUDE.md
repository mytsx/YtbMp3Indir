# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MP3Yap is a YouTube to MP3 downloader with a PyQt5 GUI. The entire application is contained in a single file: `mp3yap_gui.py`.

## Commands

### Running the Application
```bash
python mp3yap_gui.py
```

### Installing Dependencies
```bash
pip install PyQt5 yt-dlp
```

## Architecture

The application follows a single-file architecture with these key components:

1. **DownloadSignals (QObject)**: Manages thread-safe communication between the downloader and GUI
   - `progress`: Emits download percentage updates
   - `finished`: Signals download completion
   - `error`: Reports download errors
   - `status_update`: Updates status messages

2. **Downloader**: Handles the actual download logic
   - Uses yt-dlp library for YouTube downloads
   - Converts to MP3 format at 192 kbps
   - Supports both single videos and playlists
   - Downloads are saved to the `music/` directory

3. **MP3YapApp (QMainWindow)**: The main GUI window
   - Multi-line text input for URLs (one per line)
   - Progress bar showing download status
   - Threaded downloads to prevent UI freezing
   - Status label for user feedback

## Key Technical Details

- **Threading**: Downloads run in separate threads using QThread to keep the UI responsive
- **Signal/Slot Pattern**: Qt's signal/slot mechanism handles all communication between threads
- **Output Format**: MP3 files at 192 kbps, saved with sanitized filenames
- **Error Handling**: Exceptions are caught and displayed to users via the error signal

## Development Notes

- The application requires Python 3.6+ due to PyQt5 requirements
- All downloaded files are saved to the `music/` subdirectory, which is created automatically
- The GUI is built programmatically without using Qt Designer files
- URL validation and download status are handled within the Downloader class