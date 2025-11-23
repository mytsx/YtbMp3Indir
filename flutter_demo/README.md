# MP3Yap Flutter Demo

Simple Flutter demo application showing integration with FastAPI backend using HTTP + random port architecture.

## Overview

This demo demonstrates:
- **Backend Process Management**: Starting Python backend from Flutter
- **Port Discovery**: Reading stdout to discover dynamically allocated port
- **HTTP Communication**: Making API requests using Dio
- **Error Handling**: Standardized API response handling

## Features

- ✅ Auto-start backend on app launch
- ✅ Dynamic port discovery from stdout
- ✅ Simple UI for testing API endpoints
- ✅ Real-time status updates
- ✅ Error handling and display

## Prerequisites

1. **Backend must be ready:**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

2. **Flutter dependencies:**
   ```bash
   flutter pub get
   ```

## Running the Demo

### Development Mode

For development, you'll run the Python script directly instead of a bundled binary.

**Modify `backend_service.dart`:**

In the `_getBackendPath()` method, update to use Python directly:

```dart
Future<String> _getBackendPath() async {
  // For development
  return 'python3';
}
```

And update `Process.start` call:

```dart
_process = await Process.start(
  'python3',
  ['../backend/main.py'],  // Path to your backend script
  runInShell: false,
);
```

**Run the app:**
```bash
flutter run
```

### Production Mode

For production, you would:
1. Build backend binary with PyInstaller
2. Bundle it with Flutter app
3. Use platform-specific paths in `_getBackendPath()`

## Project Structure

```
flutter_demo/
├── lib/
│   ├── main.dart                          # App entry point
│   ├── core/
│   │   ├── services/
│   │   │   └── backend_service.dart       # Backend process manager
│   │   └── api/
│   │       └── api_client.dart            # HTTP API client (Dio)
│   └── screens/
│       └── demo_screen.dart               # Demo UI
├── pubspec.yaml
└── README.md
```

## How It Works

### 1. Backend Startup

```dart
final BackendService _backendService = BackendService();
await _backendService.start();
```

- Starts Python backend process
- Reads stdout line by line
- Detects `BACKEND_READY PORT=<port>`
- Stores port for API client

### 2. API Client Creation

```dart
_apiClient = ApiClient(_backendService.port!);
```

- Creates Dio client with discovered port
- Base URL: `http://127.0.0.1:<port>`
- Handles standardized API responses

### 3. Making Requests

```dart
final result = await _apiClient.startDownload(url);
// Result is automatically unwrapped from ApiResponse envelope
```

## Key Components

### BackendService

Manages backend lifecycle:
- `start()`: Start backend and discover port
- `stop()`: Gracefully shutdown backend
- `healthCheck()`: Verify backend is responsive
- `port`: Discovered port number
- `isRunning`: Backend status

### ApiClient

HTTP client wrapper:
- Automatically configures baseUrl with discovered port
- Handles ApiResponse envelope unwrapping
- Throws `ApiException` on errors
- Supports all backend endpoints

### DemoScreen

Simple UI demonstrating:
- Status display
- URL input
- Download testing
- Config retrieval
- Response display

## API Endpoints Tested

- `GET /api/health` - Health check
- `POST /api/downloads` - Start download
- `GET /api/config` - Get configuration

## Testing

1. Start the app
2. Wait for "Backend ready" status
3. Enter a YouTube URL (or any URL for testing)
4. Click "Test Download"
5. View JSON response

## Troubleshooting

### Backend not starting

- Check that Python 3 is installed
- Verify backend dependencies: `pip list | grep fastapi`
- Check backend logs in console
- Ensure port is not blocked by firewall

### Port discovery timeout

- Increase timeout in `BackendService.start()`
- Check backend stdout is not buffered
- Verify backend prints `BACKEND_READY PORT=<number>`

### API connection failed

- Check backend is actually running
- Verify port is correct
- Test with curl: `curl http://127.0.0.1:<port>/api/health`

## Production Deployment

For production apps:

1. **Bundle backend binary:**
   ```bash
   cd backend
   python build.py  # Create PyInstaller binary
   ```

2. **Include in Flutter assets:**
   - macOS: `.app/Contents/MacOS/mp3yap-backend`
   - Windows: Same folder as .exe
   - Linux: `/usr/lib/mp3yap/`

3. **Update `_getBackendPath()` to use bundled path**

See `FLUTTER_MIGRATION_PLAN.md` for complete packaging instructions.

## Next Steps

For full application:
- Implement all screens (History, Queue, Settings)
- Add Riverpod for state management
- Integrate WebSocket for progress updates
- Add proper models with fromJson/toJson
- Implement error boundaries
- Add loading states
- Create tests

## Learn More

- [Flutter Documentation](https://docs.flutter.dev/)
- [Dio Package](https://pub.dev/packages/dio)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Migration Plan](../FLUTTER_MIGRATION_PLAN.md)

## License

Same as main project.
