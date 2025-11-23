# MP3Yap Flutter App

Production Flutter application for YouTube MP3 Downloader with real-time progress tracking.

## Features

✅ **Complete Download System**
- YouTube video → MP3 conversion
- Real-time progress updates via WebSocket
- Multi-download support
- Beautiful Material Design 3 UI

✅ **State Management**
- Riverpod for reactive state
- WebSocket progress streams
- Download list management

✅ **Backend Integration**
- Automatic backend startup
- Dynamic port discovery
- HTTP API with Dio
- WebSocket progress tracking

## Architecture

### State Management (Riverpod)

**Providers:**
- `backendServiceProvider`: Backend process lifecycle
- `backendPortProvider`: Dynamic port discovery
- `apiClientProvider`: HTTP client configuration
- `downloadsProvider`: Download list state
- `startDownloadProvider`: Download action handler
- `downloadProgressProvider`: WebSocket progress stream (per download)

### Features Structure

```
lib/
├── main.dart
├── core/
│   ├── models/
│   │   └── download.dart          # Download & ProgressUpdate models
│   ├── services/
│   │   └── backend_service.dart   # Process management
│   ├── api/
│   │   └── api_client.dart        # HTTP client (Dio)
│   └── providers/
│       └── providers.dart         # Core providers
└── features/
    └── download/
        ├── providers/
        │   └── download_provider.dart    # Download-specific providers
        ├── widgets/
        │   └── download_card.dart        # Progress card widget
        └── screens/
            └── download_screen.dart      # Main screen
```

## Running the App

### Prerequisites

1. **Backend must be running:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python3 main.py
   ```

2. **Install Flutter dependencies:**
   ```bash
   cd flutter_app
   flutter pub get
   ```

### Development

```bash
flutter run
```

The app will:
1. Start backend process automatically
2. Discover port from stdout
3. Configure API client
4. Connect WebSocket for progress

## How It Works

### 1. Download Flow

```dart
// User enters URL → Provider handles download
await ref.read(startDownloadProvider(url).future);
```

**Steps:**
1. API POST to `/api/downloads` (creates download)
2. Download added to `downloadsProvider` list
3. WebSocket connection established for progress
4. Real-time UI updates via `downloadProgressProvider`

### 2. Progress Tracking

```dart
// Watch WebSocket stream for specific download
final progressStream = ref.watch(downloadProgressProvider(downloadId));
```

**Progress Types:**
- `progress`: Download percentage, speed, ETA
- `status`: Status changes (downloading, converting)
- `info`: Video title discovered
- `completed`: Download finished with file path
- `error`: Download failed with error message

### 3. Reactive UI Updates

Download card automatically updates when:
- Progress changes (percentage, speed, ETA)
- Status changes (downloading → converting → completed)
- Video title is discovered
- Download completes or fails

## UI Components

### DownloadScreen

Main screen with:
- URL input (multi-line TextField)
- Download button (with loading state)
- Active downloads counter
- Downloads list (or empty state)

### DownloadCard

Individual download card showing:
- Status icon (spinner, check, error)
- Video title
- Progress bar (when active)
- Progress percentage
- Speed and ETA
- Status text with color coding
- File path (when completed)
- Error message (when failed)

## State Flow Diagram

```
User enters URL
      ↓
startDownloadProvider
      ↓
API POST /api/downloads
      ↓
Download created
      ↓
Added to downloadsProvider
      ↓
WebSocket connected (downloadProgressProvider)
      ↓
Progress updates → UI reactive changes
      ↓
Download completes → UI shows success
```

## Error Handling

- Empty URL validation
- YouTube URL format validation
- API error display via SnackBar
- Download error display in card
- Backend connection errors

## Testing

### Manual Testing

1. Start backend: `python3 backend/main.py`
2. Run Flutter app: `flutter run`
3. Enter YouTube URL
4. Click "Start Download"
5. Watch real-time progress
6. Verify completion

### Expected Behavior

- Backend starts automatically
- Port discovered from stdout
- Download starts immediately
- Progress updates every ~500ms
- Status transitions: pending → downloading → converting → completed
- File path shown on completion

## Troubleshooting

### Backend not starting

- Check Python 3 is installed
- Verify backend dependencies: `pip list | grep -E "(fastapi|uvicorn|yt-dlp)"`
- Check backend logs in console

### WebSocket not connecting

- Verify backend is running
- Check port discovery: Should see "Backend started on port: XXXX"
- Verify WebSocket endpoint: `ws://127.0.0.1:<port>/ws/download/{id}`

### Download fails

- Check YouTube URL is valid
- Verify FFmpeg is available
- Check backend logs for yt-dlp errors
- Check internet connection

## Next Steps

For full application:
- [ ] Add History screen
- [ ] Add Queue management
- [ ] Add Settings screen
- [ ] Implement music player
- [ ] Add database persistence
- [ ] Implement proper error boundaries
- [ ] Add unit tests
- [ ] Add widget tests

## Dependencies

- `flutter_riverpod`: State management
- `dio`: HTTP client
- `web_socket_channel`: WebSocket support

## License

Same as main project.
