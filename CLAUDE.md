# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MP3Yap is a YouTube MP3 downloader application with a modern Flutter desktop frontend and FastAPI Python backend. The project migrated from a PyQt5 desktop app to this Flutter + FastAPI architecture for better UI/UX and cross-platform support.

## Commands

### Running the Application

**Backend (FastAPI):**
```bash
cd backend
../.venv/bin/python main.py
# Or if venv is active:
python main.py
```
Backend writes port to `.backend_port` file for Flutter auto-discovery.

**Frontend (Flutter):**
```bash
cd flutter_app
flutter run -d macos  # or -d windows, -d linux
```
Flutter auto-starts backend if not already running (using venv python).

**Full Stack (recommended):**
Start Flutter app - it will automatically detect or start the backend.

### Installing Dependencies

**Backend:**
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
cd flutter_app
flutter pub get
```

## Architecture Overview

```
Flutter Frontend (Dart + Riverpod)
        ↕ REST API + WebSocket
FastAPI Backend (Python)
        ↕
yt-dlp + FFmpeg + SQLite
```

### Backend (`backend/`)

| Path | Purpose |
|------|---------|
| `main.py` | FastAPI entry point with dynamic port discovery (TTS pattern) |
| `api/routes/` | REST endpoints: downloads, history, queue, config |
| `api/websocket.py` | Real-time download progress via WebSocket |
| `services/download_service.py` | Thread-safe job queue with worker pool (3 concurrent) |
| `database/` | SQLite operations for history and queue |

**Key Patterns:**
- Dynamic port discovery via `.backend_port` file
- Thread-safe download queue with `threading.Lock` and `queue.Queue`
- WebSocket for real-time progress updates
- Absolute file paths for cross-platform compatibility

### Frontend (`flutter_app/lib/`)

| Path | Purpose |
|------|---------|
| `main.dart` | App entry, backend auto-start, navigation |
| `core/services/backend_service.dart` | Backend lifecycle management, health checks |
| `core/providers/` | Riverpod providers for state management |
| `features/download/` | Download screen, providers, widgets |
| `features/history/` | History list with audio playback |
| `features/player/` | Audio player state management |
| `features/settings/` | App configuration |

**Key Patterns:**
- Riverpod for state management
- Auto-detect existing backend before starting new process
- venv python detection for backend startup
- Provider invalidation for reactive UI updates

### macOS Configuration (`flutter_app/macos/`)

| File | Configuration |
|------|---------------|
| `Runner/MainFlutterWindow.swift` | Window size: min 800x700, initial 1000x750 |

## Database Schema

### download_history
```sql
id, video_title, file_name, file_path, url, format,
file_size, duration, channel_name, downloaded_at, status, is_deleted
```

### download_queue
```sql
id, url, video_title, priority, position, status,
added_at, started_at, completed_at, error_message, is_deleted
```

## Development Notes

### Backend Auto-Start Flow
1. Flutter checks for `.backend_port` file
2. If found, health check existing backend
3. If not responsive, delete port file and start new process
4. Use venv python (`.venv/bin/python`) if available, fallback to `python3`
5. Wait up to 30s for port file, 90s for health check

### Thread Safety
- Backend uses worker pool (3 threads) with job queue
- `downloads_lock` protects active downloads dict
- WebSocket updates sent from worker threads

### File Paths
- Backend converts all paths to absolute: `os.path.abspath(output_dir)`
- Flutter validates file existence before audio playback
- Legacy relative paths converted to absolute on-the-fly

### Soft Delete Pattern
- All delete operations set `is_deleted = 1` instead of removing records
- Queries filter with `WHERE is_deleted = 0`
- Enables potential recovery of "deleted" items

## Legacy Code

The original PyQt5 desktop application is archived in:
- `python_desktop/` - Full PyQt5 source code
- `archive/python_desktop.zip` - Backup archive

Root `requirements.txt` contains PyQt5 dependencies for the legacy app.
Backend dependencies are in `backend/requirements.txt`.
