# MP3 Yap

A modern YouTube to MP3 downloader desktop application built with Flutter and Python.

## Overview

MP3 Yap is a cross-platform desktop application that allows you to download YouTube videos as MP3 files and convert local audio/video files to MP3 format. Built with a modern Flutter frontend and FastAPI Python backend.

## Features

### Download
- Download YouTube videos as MP3
- Real-time download progress via WebSocket
- Queue management for multiple downloads
- Concurrent downloads (up to 3 simultaneous)

### Convert
- Convert local audio/video files to MP3
- Supports 30+ formats (MP4, MKV, WAV, FLAC, M4A, etc.)
- Real-time conversion progress

### History
- Browse download history
- Play downloaded MP3s with built-in player
- Search and filter history
- Quick access to file location

### Settings
- Configurable audio quality (128/192/256/320 kbps)
- Custom download folder
- Light/Dark/System theme
- Notification sounds
- History retention settings

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flutter Frontend                      │
│              (Dart + Riverpod + Material 3)             │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API + WebSocket
┌─────────────────────┴───────────────────────────────────┐
│                    FastAPI Backend                       │
│                      (Python 3.11+)                      │
├─────────────────────────────────────────────────────────┤
│  yt-dlp          │  FFmpeg          │  SQLite           │
│  (YouTube)       │  (Conversion)    │  (Database)       │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Flutter 3.x | Cross-platform UI |
| State | Riverpod | State management |
| Backend | FastAPI | REST API server |
| Download | yt-dlp | YouTube downloads |
| Audio | FFmpeg | Audio conversion |
| Database | SQLite | Local storage |
| IPC | WebSocket | Real-time updates |

## Requirements

### System
- macOS 10.14+ / Windows 10+ / Linux
- 4GB RAM minimum
- 500MB disk space

### Development
- Flutter 3.x
- Python 3.11 or 3.12
- FFmpeg (bundled via yt-dlp)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/mehmetyerli/mp3yap.git
cd mp3yap
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup

```bash
cd flutter_app
flutter pub get
```

## Running the Application

### Option 1: Run Flutter (Recommended)

Flutter automatically starts the backend:

```bash
cd flutter_app
flutter run -d macos  # or -d windows, -d linux
```

### Option 2: Run Separately

**Terminal 1 - Backend:**
```bash
cd backend
../.venv/bin/python main.py
```

**Terminal 2 - Frontend:**
```bash
cd flutter_app
flutter run -d macos
```

## Project Structure

```
mp3yap/
├── flutter_app/                 # Flutter frontend
│   ├── lib/
│   │   ├── core/               # Core services, models, providers
│   │   ├── features/           # Feature modules
│   │   │   ├── download/       # YouTube download
│   │   │   ├── convert/        # File conversion
│   │   │   ├── history/        # Download history
│   │   │   ├── settings/       # App settings
│   │   │   └── player/         # Audio player
│   │   └── shared/             # Shared widgets
│   └── macos/                  # macOS platform config
│
├── backend/                     # Python backend
│   ├── main.py                 # FastAPI entry point
│   ├── api/                    # API routes
│   ├── services/               # Business logic
│   ├── database/               # SQLite operations
│   └── utils/                  # Utilities
│
└── python_desktop/             # Legacy PyQt5 app (archived)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/downloads` | Start download |
| GET | `/api/downloads` | List active downloads |
| DELETE | `/api/downloads/{id}` | Cancel download |
| GET | `/api/history` | Get download history |
| DELETE | `/api/history/{id}` | Delete history item |
| POST | `/api/conversions` | Start conversion |
| GET | `/api/config` | Get settings |
| PUT | `/api/config` | Update settings |
| WS | `/ws` | Real-time progress |

## Database Schema

### download_history
```sql
id, video_title, file_name, file_path, url, format,
file_size, duration, channel_name, channel_url,
downloaded_at, status, is_deleted
```

### download_queue
```sql
id, url, video_title, priority, position, status,
added_at, started_at, completed_at, error_message, is_deleted
```

## Development

### Code Style

- Flutter: Follow [Effective Dart](https://dart.dev/guides/language/effective-dart)
- Python: Follow [PEP 8](https://pep8.org/)

### Running Tests

```bash
# Flutter tests
cd flutter_app
flutter test

# Python tests
cd backend
pytest
```

### Building for Release

```bash
cd flutter_app
flutter build macos  # or windows, linux
```

## Known Limitations

- App Store distribution not possible (requires sandbox, but app spawns Python process)
- Distribution via DMG with Apple Notarization or direct download

## License

MIT License - See [LICENSE.txt](LICENSE.txt)

## Author

**Mehmet Yerli**
- Website: [mehmetyerli.com](https://mehmetyerli.com)
- Email: iletisim@mehmetyerli.com
- GitHub: [@mehmetyerli](https://github.com/mehmetyerli)

## Disclaimer

This software is provided "as is" without warranty. Users are responsible for ensuring they have the right to download content. This tool is for educational purposes and personal use only.
