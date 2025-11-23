# Flutter App Development Guide

## Quick Start (Recommended)

The Flutter app will **automatically detect** if the backend is already running. The easiest way to develop:

### Option 1: Manual Backend + Auto-Detect (Recommended)

1. **Start backend manually:**
   ```bash
   cd backend
   uvicorn main:app --port 8000 --reload
   ```

2. **Start Flutter app:**
   ```bash
   cd flutter_app
   flutter run -d macos
   ```

The app will detect the running backend on port 8000 and connect automatically!

### Option 2: Automatic Backend Start

If you want Flutter to start the backend automatically:

```bash
cd flutter_app
PROJECT_ROOT=/Users/yerli/Developer/mehmetyerli/mp3yap flutter run -d macos
```

> **Note:** This requires the app sandbox to be disabled (already done in DebugProfile.entitlements).

## Requirements

- **Flutter** 3.0+ installed
- **Python 3.11+** with dependencies:
  ```bash
  cd ../backend
  pip install -r requirements.txt
  ```
- **uvicorn** available in PATH:
  ```bash
  pip install uvicorn
  ```

## Architecture

```
┌─────────────────┐
│  Flutter App    │
│  (Port 8000)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────┐
│  Backend API    │
│  (FastAPI)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  yt-dlp +       │
│  FFmpeg         │
└─────────────────┘
```

### How It Works

1. **App Startup:**
   - `main.dart` calls `BackendService.start()`
   - Service checks if backend is already running (healthCheck on port 8000)
   - If running → uses existing backend
   - If not → attempts to start uvicorn (requires PROJECT_ROOT env var)

2. **Backend Communication:**
   - **HTTP API:** `/api/downloads`, `/api/history`, `/api/config`
   - **WebSocket:** `/ws/download/{id}` for real-time progress

3. **Fixed Port:**
   - Development uses **port 8000** (fixed)
   - No port discovery needed
   - Backend must run on port 8000

## Troubleshooting

### "Connection refused" Error

Backend is not running. Start it manually:
```bash
cd backend
uvicorn main:app --port 8000
```

### "Operation not permitted" (Exit Code 126)

macOS prevented spawning uvicorn. Solutions:
- Use **Option 1** (manual backend start) - Recommended!
- Check `DebugProfile.entitlements` has sandbox disabled (`<false/>`)
- Run with PROJECT_ROOT environment variable

### Backend Not Found

If using automatic start, set PROJECT_ROOT:
```bash
PROJECT_ROOT=$(pwd) flutter run -d macos
```

### Port Already in Use

Kill existing process on port 8000:
```bash
lsof -ti:8000 | xargs kill -9
```

## Development Workflow

### Recommended Daily Workflow

```bash
# Terminal 1: Backend (with auto-reload)
cd backend
uvicorn main:app --port 8000 --reload

# Terminal 2: Flutter (with hot reload)
cd flutter_app
flutter run -d macos
```

Now you can:
- Edit backend code → automatic reload
- Edit Flutter code → hot reload (press `r` in terminal)

### Clean Rebuild

```bash
cd flutter_app
flutter clean
flutter pub get
flutter run -d macos
```

## Project Structure

```
flutter_app/
├── lib/
│   ├── main.dart                 # App entry + backend startup
│   ├── core/
│   │   ├── services/
│   │   │   └── backend_service.dart  # Backend process management
│   │   ├── api/
│   │   │   └── api_client.dart       # HTTP client (Dio)
│   │   └── providers/
│   │       └── providers.dart         # Riverpod providers
│   └── features/
│       ├── download/              # Download feature
│       ├── history/               # History feature
│       └── settings/              # Settings feature
├── macos/
│   └── Runner/
│       └── DebugProfile.entitlements  # Sandbox settings
└── docs/
    └── DEVELOPMENT.md            # This file
```

## Testing

### Manual Test

1. Start backend
2. Start Flutter app
3. Enter YouTube URL: `https://youtu.be/DM1CLCgqFGI`
4. Click "Start Download"
5. Watch real-time progress
6. Verify completion

### Expected Behavior

- ✅ Backend auto-detected or auto-started
- ✅ Download starts immediately
- ✅ Progress updates in real-time via WebSocket
- ✅ File saved to `~/Music/` (default)
- ✅ History tab shows completed downloads

## Production Considerations

For release builds, we need to decide:

1. **Bundle Backend:** Use PyInstaller to create standalone executable
   - Pros: No Python dependency
   - Cons: Larger app size

2. **Separate Backend:** User installs Python + dependencies
   - Pros: Smaller Flutter app
   - Cons: Complex user setup

Currently: Development mode only (manual backend).

## Useful Commands

```bash
# Flutter
flutter doctor                  # Check Flutter installation
flutter devices                 # List available devices
flutter pub get                 # Install dependencies
flutter clean                   # Clean build artifacts
flutter build macos --release   # Build release

# Backend
pip list | grep uvicorn         # Check uvicorn installed
lsof -i :8000                   # Check port 8000 usage
curl http://localhost:8000/api/config  # Test backend

# Development
flutter run -d macos --verbose  # Verbose logging
flutter run -d macos --release  # Release mode test
```

## Next Steps

- [ ] Implement remaining features (Queue, Player)
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Decide on production backend strategy
- [ ] Create release build pipeline
