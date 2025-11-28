# MP3Yap Backend

FastAPI backend for MP3Yap Flutter application.

## Overview

This backend provides REST API endpoints and WebSocket support for the YouTube MP3 downloader application. It uses **random port allocation** (port=0) to avoid port conflicts and communicates the selected port via stdout to the Flutter frontend.

## Features

- REST API with standardized JSON response envelope
- WebSocket support for real-time progress updates
- Random port allocation (no port conflicts)
- CORS configured for localhost only
- Type-safe with Pydantic models

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Server

```bash
python3 main.py
```

Expected output:
```
BACKEND_READY PORT=<random_port>
INFO:     Started server process [12345]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:<random_port>
```

### Test API

Once the server is running, you can test the endpoints:

```bash
# Health check
curl http://127.0.0.1:<port>/api/health

# Get configuration
curl http://127.0.0.1:<port>/api/config

# Start download
curl -X POST http://127.0.0.1:<port>/api/downloads \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=dQw4w9WgXcQ", "quality": "192"}'
```

## API Endpoints

### Health Check
- `GET /api/health` - Server health status

### Downloads
- `POST /api/downloads` - Start new download
- `GET /api/downloads` - List active downloads
- `GET /api/downloads/{id}` - Get download details
- `DELETE /api/downloads/{id}` - Cancel download

### History
- `GET /api/history` - Get download history
- `GET /api/history/{id}` - Get specific history item
- `POST /api/history/{id}/redownload` - Re-download from history
- `DELETE /api/history/{id}` - Soft delete history item

### Queue
- `GET /api/queue` - Get queue items
- `POST /api/queue` - Add to queue
- `PATCH /api/queue/{id}/priority` - Update priority
- `PATCH /api/queue/{id}/position` - Update position
- `DELETE /api/queue/{id}` - Remove from queue

### Config
- `GET /api/config` - Get configuration
- `PATCH /api/config` - Update configuration

### WebSocket
- `WS /ws/download/{download_id}` - Real-time progress updates

## Response Format

All API endpoints return responses in this format:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

On error:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Project Structure

```
backend/
├── main.py                 # Entry point (port=0, stdout logging)
├── api/
│   ├── __init__.py
│   ├── models.py           # Pydantic models
│   ├── routes/
│   │   ├── downloads.py    # Download endpoints
│   │   ├── history.py      # History endpoints
│   │   ├── queue.py        # Queue endpoints
│   │   └── config.py       # Config endpoints
│   └── websocket.py        # WebSocket handlers
└── requirements.txt
```

## How Port Discovery Works

1. Backend binds to port 0 (OS selects available port)
2. Backend prints `BACKEND_READY PORT=<port>` to stdout
3. Flutter reads stdout and extracts port number
4. Flutter configures Dio client with `http://127.0.0.1:<port>`

This eliminates port conflicts without requiring complex IPC mechanisms.

## Development Notes

### Current Status
- Basic API structure implemented
- Standardized response envelope
- WebSocket manager ready
- In-memory storage (to be replaced with database)

### TODO
- Integrate with existing `core/downloader.py`
- Connect to SQLite database
- Implement actual download logic
- Add background task processing
- Error handling improvements

## Testing

### Automated Tests

Run the integration test suite:

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run tests
python3 tests/test_backend.py
```

Expected output:
```
============================================================
Backend Integration Tests
============================================================
🧪 Test 1: Backend startup and port discovery...
   ✅ PASS: Backend started on port 62152
🧪 Test 2: Health endpoint...
   ✅ PASS: Health check successful
...
✅ All tests passed!
```

### Manual Testing

Run the backend and test with curl or Postman:

```bash
# Terminal 1: Run backend
python3 main.py

# Terminal 2: Test (replace <port> with actual port from output)
curl http://127.0.0.1:<port>/api/health
```

## Integration with Flutter

Flutter will:
1. Start backend process: `Process.start('mp3yap-backend')`
2. Read stdout to get port
3. Configure API client with discovered port
4. Make HTTP requests to `http://127.0.0.1:<port>/api/*`

See `FLUTTER_MIGRATION_PLAN.md` for complete integration details.

## License

Same as main project.
