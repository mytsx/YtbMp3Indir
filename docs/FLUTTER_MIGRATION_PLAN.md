# PyQt5 → Flutter+FastAPI Migration Planı
## HTTP + Random Port Yaklaşımı

## Genel Bakış
- **Hedef**: YouTube MP3 İndirici'yi tamamen Flutter (frontend) + FastAPI (backend) mimarisine migrate etmek
- **Platform**: macOS, Windows, Linux (full cross-platform)
- **Yaklaşım**: Direkt tam migration (PyQt5'i sil)
- **İletişim**: HTTP (localhost) + JSON API
- **Port Yönetimi**: Random port allocation (port=0) + stdout discovery
- **Tahmini Süre**: 4-6 hafta

### 🔥 Neden HTTP + Random Port?

**Avantajlar:**
- ✅ **Port çakışması YOK** - OS otomatik boş port seçer (port=0)
- ✅ **Basit ve proven** - Standard HTTP, WebSocket kullanımı
- ✅ **Cross-platform** - Tüm platformlarda aynı kod
- ✅ **Kolay debug** - HTTP tools (Postman, curl) kullanılabilir
- ✅ **No extra dependencies** - Dart stdlib yeterli
- ✅ **Pragmatic** - 1-2ms latency farkı hissedilmez (bottleneck: yt-dlp 10-30s + FFmpeg 5-15s)

**Architecture:**
```
Backend → uvicorn.run(app, host='127.0.0.1', port=0)
Backend → stdout'a yazar: "BACKEND_READY PORT=12345"
Flutter → Backend'i Process.start ile başlatır
Flutter → stdout'tan port'u okur
Flutter → Dio baseUrl = http://127.0.0.1:12345
```

---

## Phase 1: FastAPI Backend API (1-2 hafta)

### 1.1 Proje Yapısı Oluşturma

```
backend/
├── main.py                    # FastAPI entry point + uvicorn startup
├── api/
│   ├── __init__.py
│   ├── models.py              # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── downloads.py       # /api/downloads
│   │   ├── history.py         # /api/history
│   │   ├── queue.py           # /api/queue
│   │   └── config.py          # /api/config
│   └── websocket.py           # WebSocket endpoint
├── core/                      # Moved from root
│   └── downloader.py
├── database/                  # Moved from root
│   └── manager.py
├── utils/                     # Moved from root
│   └── config.py
└── requirements.txt
```

### 1.2 Backend Entry Point

```python
# backend/main.py
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import downloads, history, queue, config
from api.websocket import websocket_router

app = FastAPI(title="MP3Yap Backend", version="3.0.0")

# CORS (localhost only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:*", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(websocket_router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

def main():
    """Start server with random port and print to stdout"""
    import socket

    # Let OS choose available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]

    # Print port to stdout for Flutter to read
    print(f"BACKEND_READY PORT={port}", flush=True)
    sys.stdout.flush()

    # Start uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        access_log=False  # Reduce noise
    )

if __name__ == "__main__":
    main()
```

### 1.3 API Response Envelope (Standardized)

```python
# backend/api/models.py
from pydantic import BaseModel
from typing import Any, Optional

class ErrorDetail(BaseModel):
    code: str
    message: str

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None

# Usage in routes:
@router.post("/")
async def create_download(url: str, quality: str = "192"):
    try:
        download = await download_service.start_download(url, quality)
        return ApiResponse(
            success=True,
            data=download.dict()
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ErrorDetail(code="DOWNLOAD_FAILED", message=str(e))
        )
```

### 1.4 REST API Endpoints

#### Downloads
```python
POST   /api/downloads              # Yeni indirme başlat
GET    /api/downloads              # Aktif indirmeleri listele
GET    /api/downloads/{id}         # İndirme detayı
DELETE /api/downloads/{id}         # İndirmeyi iptal et

# Request body (POST):
{
  "url": "https://youtube.com/watch?v=...",
  "quality": "192"  // kbps
}

# Response:
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "url": "...",
    "status": "downloading",
    "progress": 0,
    "video_title": "Song Name"
  },
  "error": null
}
```

#### History
```python
GET    /api/history               # Geçmiş listesi
GET    /api/history/{id}          # Geçmiş detayı
POST   /api/history/{id}/redownload
DELETE /api/history/{id}          # Soft delete

# Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "video_title": "Song Name",
      "file_name": "song.mp3",
      "file_path": "/path/to/music/song.mp3",
      "downloaded_at": "2025-11-23T10:00:00",
      "file_size": 5242880,
      "duration": 180
    }
  ],
  "error": null
}
```

#### Queue
```python
GET    /api/queue                 # Kuyruk listesi
POST   /api/queue                 # Kuyruğa ekle
PATCH  /api/queue/{id}/priority   # Öncelik değiştir
PATCH  /api/queue/{id}/position   # Pozisyon değiştir
DELETE /api/queue/{id}            # Kuyruktan çıkar
```

#### Config
```python
GET    /api/config                # Ayarları getir
PATCH  /api/config                # Ayarları güncelle

# Response:
{
  "success": true,
  "data": {
    "output_dir": "/Users/yerli/Music",
    "quality": "192",
    "auto_open": true,
    "language": "tr"
  },
  "error": null
}
```

### 1.5 WebSocket for Progress Updates

```python
# backend/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio

websocket_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, download_id: str, websocket: WebSocket):
        await websocket.accept()
        if download_id not in self.active_connections:
            self.active_connections[download_id] = []
        self.active_connections[download_id].append(websocket)

    def disconnect(self, download_id: str, websocket: WebSocket):
        if download_id in self.active_connections:
            self.active_connections[download_id].remove(websocket)

    async def broadcast(self, download_id: str, message: dict):
        if download_id in self.active_connections:
            for connection in self.active_connections[download_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@websocket_router.websocket("/ws/download/{download_id}")
async def websocket_endpoint(websocket: WebSocket, download_id: str):
    await manager.connect(download_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(download_id, websocket)

# Usage in downloader:
async def progress_hook(data: dict):
    download_id = data['download_id']
    await manager.broadcast(download_id, {
        'type': 'progress',
        'progress': data['progress'],
        'speed': data['speed'],
        'eta': data['eta']
    })
```

### 1.6 Mevcut Kodu Wrap Etme

```python
# backend/core/downloader.py (adapted)
from api.websocket import manager

class DownloadService:
    async def start_download(self, url: str, quality: str):
        download_id = str(uuid.uuid4())

        # Create download record
        download = await db.create_download(url, quality, download_id)

        # Start download in background task
        asyncio.create_task(self._download_worker(download_id, url, quality))

        return download

    async def _download_worker(self, download_id: str, url: str, quality: str):
        def progress_hook(d):
            if d['status'] == 'downloading':
                asyncio.run(manager.broadcast(download_id, {
                    'type': 'progress',
                    'progress': d.get('_percent_str', '0%'),
                    'speed': d.get('_speed_str', 'N/A'),
                }))

        # Use existing yt-dlp logic
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'progress_hooks': [progress_hook],
        }

        # ... rest of download logic
```

---

## Phase 2: Flutter Project Setup (3-5 gün)

### 2.1 Flutter Desktop Projesi
```bash
flutter create --platforms=macos,windows,linux mp3yap_flutter
cd mp3yap_flutter
```

### 2.2 Dependencies
```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.4.0

  # HTTP & WebSocket
  dio: ^5.4.0
  web_socket_channel: ^2.4.0

  # UI & Utils
  window_manager: ^0.3.7
  file_picker: ^6.1.1
  path_provider: ^2.1.1
  url_launcher: ^6.2.2

  # Routing
  go_router: ^13.0.0
```

### 2.3 Proje Yapısı
```
lib/
├── main.dart                      # Entry point
├── app.dart                       # App widget + router
├── core/
│   ├── api/
│   │   ├── api_client.dart        # Dio HTTP client
│   │   └── models/                # API response models
│   ├── services/
│   │   └── backend_service.dart   # Backend process manager
│   └── providers/
│       ├── backend_provider.dart
│       └── api_provider.dart
├── features/
│   ├── download/
│   │   ├── providers/
│   │   │   └── download_provider.dart
│   │   ├── widgets/
│   │   │   ├── url_input.dart
│   │   │   └── progress_card.dart
│   │   └── screens/
│   │       └── download_screen.dart
│   ├── history/
│   ├── queue/
│   └── settings/
└── shared/
    └── widgets/
```

### 2.4 Backend Process Manager

```dart
// lib/core/services/backend_service.dart
import 'dart:async';
import 'dart:convert';
import 'dart:io';

class BackendService {
  Process? _process;
  int? _port;

  int? get port => _port;
  bool get isRunning => _process != null && _port != null;

  Future<void> start() async {
    if (isRunning) return;

    final backendPath = await _getBackendPath();

    // Start backend process
    _process = await Process.start(
      backendPath,
      [],
      runInShell: false,
    );

    // Listen to stdout for port discovery
    final portCompleter = Completer<int>();

    _process!.stdout
        .transform(utf8.decoder)
        .transform(LineSplitter())
        .listen((line) {
      print('[Backend] $line');

      // Parse "BACKEND_READY PORT=12345"
      if (line.startsWith('BACKEND_READY PORT=')) {
        final portStr = line.split('=')[1].trim();
        final port = int.tryParse(portStr);
        if (port != null && !portCompleter.isCompleted) {
          portCompleter.complete(port);
        }
      }
    });

    _process!.stderr
        .transform(utf8.decoder)
        .transform(LineSplitter())
        .listen((line) {
      print('[Backend Error] $line');
    });

    // Wait for port (timeout: 10 seconds)
    _port = await portCompleter.future.timeout(
      const Duration(seconds: 10),
      onTimeout: () {
        throw Exception('Backend did not report port within 10 seconds');
      },
    );

    print('Backend started on port: $_port');
  }

  Future<String> _getBackendPath() async {
    // For development: use python script directly
    if (Platform.environment.containsKey('FLUTTER_DEV')) {
      return 'python3';  // Will need to pass main.py as argument
    }

    // For production: bundled binary
    if (Platform.isMacOS) {
      return 'mp3yap-backend';  // In .app/Contents/MacOS/
    } else if (Platform.isWindows) {
      return 'mp3yap-backend.exe';
    } else {
      return './mp3yap-backend';
    }
  }

  Future<void> stop() async {
    if (_process != null) {
      _process!.kill(ProcessSignal.sigterm);
      await _process!.exitCode.timeout(
        const Duration(seconds: 5),
        onTimeout: () {
          _process!.kill(ProcessSignal.sigkill);
          return -1;
        },
      );
      _process = null;
      _port = null;
    }
  }
}
```

### 2.5 API Client (Dio)

```dart
// lib/core/api/api_client.dart
import 'package:dio/dio.dart';

class ApiClient {
  final Dio _dio;

  ApiClient(int port)
      : _dio = Dio(BaseOptions(
          baseUrl: 'http://127.0.0.1:$port',
          connectTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            'Content-Type': 'application/json',
          },
        )) {
    // Add logging interceptor (dev only)
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }

  // Generic response handler
  Future<T> _handleResponse<T>(
    Future<Response> request,
    T Function(dynamic) fromJson,
  ) async {
    try {
      final response = await request;
      final data = response.data;

      if (data['success'] == true) {
        return fromJson(data['data']);
      } else {
        throw ApiException(
          code: data['error']['code'],
          message: data['error']['message'],
        );
      }
    } on DioException catch (e) {
      throw ApiException(
        code: 'NETWORK_ERROR',
        message: e.message ?? 'Unknown error',
      );
    }
  }

  // Downloads
  Future<Download> startDownload(String url, {String quality = '192'}) {
    return _handleResponse(
      _dio.post('/api/downloads', data: {
        'url': url,
        'quality': quality,
      }),
      (data) => Download.fromJson(data),
    );
  }

  Future<List<Download>> getDownloads() {
    return _handleResponse(
      _dio.get('/api/downloads'),
      (data) => (data as List).map((e) => Download.fromJson(e)).toList(),
    );
  }

  Future<Download> getDownload(String id) {
    return _handleResponse(
      _dio.get('/api/downloads/$id'),
      (data) => Download.fromJson(data),
    );
  }

  Future<void> cancelDownload(String id) {
    return _handleResponse(
      _dio.delete('/api/downloads/$id'),
      (_) => null,
    );
  }

  // History
  Future<List<HistoryItem>> getHistory() {
    return _handleResponse(
      _dio.get('/api/history'),
      (data) => (data as List).map((e) => HistoryItem.fromJson(e)).toList(),
    );
  }

  Future<Download> redownload(int id) {
    return _handleResponse(
      _dio.post('/api/history/$id/redownload'),
      (data) => Download.fromJson(data),
    );
  }

  // Config
  Future<AppConfig> getConfig() {
    return _handleResponse(
      _dio.get('/api/config'),
      (data) => AppConfig.fromJson(data),
    );
  }

  Future<AppConfig> updateConfig(Map<String, dynamic> updates) {
    return _handleResponse(
      _dio.patch('/api/config', data: updates),
      (data) => AppConfig.fromJson(data),
    );
  }
}

class ApiException implements Exception {
  final String code;
  final String message;

  ApiException({required this.code, required this.message});

  @override
  String toString() => 'ApiException($code): $message';
}
```

### 2.6 API Models

```dart
// lib/core/api/models/download.dart
class Download {
  final String id;
  final String url;
  final String status;
  final int progress;
  final String? videoTitle;
  final String? error;

  Download({
    required this.id,
    required this.url,
    required this.status,
    required this.progress,
    this.videoTitle,
    this.error,
  });

  factory Download.fromJson(Map<String, dynamic> json) {
    return Download(
      id: json['id'],
      url: json['url'],
      status: json['status'],
      progress: json['progress'] ?? 0,
      videoTitle: json['video_title'],
      error: json['error'],
    );
  }
}

// lib/core/api/models/history_item.dart
class HistoryItem {
  final int id;
  final String videoTitle;
  final String fileName;
  final String filePath;
  final DateTime downloadedAt;
  final int? fileSize;
  final int? duration;

  HistoryItem({
    required this.id,
    required this.videoTitle,
    required this.fileName,
    required this.filePath,
    required this.downloadedAt,
    this.fileSize,
    this.duration,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id'],
      videoTitle: json['video_title'],
      fileName: json['file_name'],
      filePath: json['file_path'],
      downloadedAt: DateTime.parse(json['downloaded_at']),
      fileSize: json['file_size'],
      duration: json['duration'],
    );
  }
}
```

### 2.7 Riverpod Providers

```dart
// lib/core/providers/backend_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/backend_service.dart';

final backendServiceProvider = Provider<BackendService>((ref) {
  final service = BackendService();

  ref.onDispose(() {
    service.stop();
  });

  return service;
});

final backendPortProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(backendServiceProvider);
  await service.start();
  return service.port!;
});

// lib/core/providers/api_provider.dart
import '../api/api_client.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  final portAsync = ref.watch(backendPortProvider);

  return portAsync.when(
    data: (port) => ApiClient(port),
    loading: () => throw Exception('Backend not ready'),
    error: (err, stack) => throw err,
  );
});
```

### 2.8 WebSocket Progress Stream

```dart
// lib/features/download/providers/download_provider.dart
import 'package:web_socket_channel/web_socket_channel.dart';

final downloadProgressProvider = StreamProvider.family<DownloadProgress, String>(
  (ref, downloadId) {
    final port = ref.watch(backendPortProvider).value!;
    final wsUrl = 'ws://127.0.0.1:$port/ws/download/$downloadId';

    final channel = WebSocketChannel.connect(Uri.parse(wsUrl));

    ref.onDispose(() {
      channel.sink.close();
    });

    return channel.stream.map((data) {
      final json = jsonDecode(data);
      return DownloadProgress.fromJson(json);
    });
  },
);

class DownloadProgress {
  final String type;
  final int? progress;
  final String? speed;
  final String? eta;

  DownloadProgress({
    required this.type,
    this.progress,
    this.speed,
    this.eta,
  });

  factory DownloadProgress.fromJson(Map<String, dynamic> json) {
    return DownloadProgress(
      type: json['type'],
      progress: json['progress'],
      speed: json['speed'],
      eta: json['eta'],
    );
  }
}
```

---

## Phase 3: UI Implementation (2-3 hafta)

### 3.1 Main App Structure

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:window_manager/window_manager.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Desktop window setup
  await windowManager.ensureInitialized();
  await windowManager.setTitle('MP3 Yap');
  await windowManager.setMinimumSize(const Size(900, 600));

  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

// lib/app.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'features/download/screens/download_screen.dart';
import 'features/history/screens/history_screen.dart';
import 'features/queue/screens/queue_screen.dart';
import 'features/settings/screens/settings_screen.dart';

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = GoRouter(
      routes: [
        ShellRoute(
          builder: (context, state, child) {
            return MainLayout(child: child);
          },
          routes: [
            GoRoute(
              path: '/',
              builder: (context, state) => const DownloadScreen(),
            ),
            GoRoute(
              path: '/history',
              builder: (context, state) => const HistoryScreen(),
            ),
            GoRoute(
              path: '/queue',
              builder: (context, state) => const QueueScreen(),
            ),
            GoRoute(
              path: '/settings',
              builder: (context, state) => const SettingsScreen(),
            ),
          ],
        ),
      ],
    );

    return MaterialApp.router(
      title: 'MP3 Yap',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      routerConfig: router,
    );
  }
}

class MainLayout extends StatelessWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Sidebar navigation
          NavigationRail(
            selectedIndex: _selectedIndex(context),
            onDestinationSelected: (index) => _navigate(context, index),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.download),
                label: Text('İndir'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.history),
                label: Text('Geçmiş'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.queue_music),
                label: Text('Kuyruk'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.settings),
                label: Text('Ayarlar'),
              ),
            ],
          ),
          const VerticalDivider(thickness: 1, width: 1),
          // Main content
          Expanded(child: child),
        ],
      ),
    );
  }

  int _selectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    switch (location) {
      case '/':
        return 0;
      case '/history':
        return 1;
      case '/queue':
        return 2;
      case '/settings':
        return 3;
      default:
        return 0;
    }
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/history');
        break;
      case 2:
        context.go('/queue');
        break;
      case 3:
        context.go('/settings');
        break;
    }
  }
}
```

### 3.2 Download Screen (Demo)

```dart
// lib/features/download/screens/download_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/api_provider.dart';

class DownloadScreen extends ConsumerStatefulWidget {
  const DownloadScreen({super.key});

  @override
  ConsumerState<DownloadScreen> createState() => _DownloadScreenState();
}

class _DownloadScreenState extends ConsumerState<DownloadScreen> {
  final _urlController = TextEditingController();
  String? _response;
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'YouTube MP3 İndir',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 24),

          // URL Input
          TextField(
            controller: _urlController,
            decoration: const InputDecoration(
              labelText: 'YouTube URL',
              hintText: 'https://youtube.com/watch?v=...',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),

          // Download Button
          FilledButton.icon(
            onPressed: _isLoading ? null : _handleDownload,
            icon: _isLoading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.download),
            label: Text(_isLoading ? 'İndiriliyor...' : 'İndir'),
          ),
          const SizedBox(height: 24),

          // Response Display
          if (_response != null)
            Expanded(
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: SingleChildScrollView(
                    child: SelectableText(
                      _response!,
                      style: const TextStyle(fontFamily: 'monospace'),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _handleDownload() async {
    if (_urlController.text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _response = null;
    });

    try {
      final api = ref.read(apiClientProvider);
      final download = await api.startDownload(_urlController.text);

      setState(() {
        _response = '''
İndirme başlatıldı!

ID: ${download.id}
URL: ${download.url}
Durum: ${download.status}
İlerleme: ${download.progress}%
${download.videoTitle != null ? 'Başlık: ${download.videoTitle}' : ''}
''';
      });
    } catch (e) {
      setState(() {
        _response = 'Hata: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}
```

---

## Phase 4: Testing & Type Safety

### 4.1 Backend Testing

```python
# backend/tests/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_start_download():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/downloads", json={
            "url": "https://youtube.com/watch?v=test",
            "quality": "192"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
```

### 4.2 Flutter Testing

```dart
// test/api_client_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('ApiClient', () {
    test('startDownload returns Download on success', () async {
      // Mock Dio response
      final mockDio = MockDio();
      when(mockDio.post(any, data: anyNamed('data')))
          .thenAnswer((_) async => Response(
                data: {
                  'success': true,
                  'data': {
                    'id': 'test-id',
                    'url': 'https://youtube.com/watch?v=test',
                    'status': 'downloading',
                    'progress': 0,
                  },
                },
                statusCode: 200,
                requestOptions: RequestOptions(path: ''),
              ));

      final client = ApiClient(8000);
      final download = await client.startDownload('https://youtube.com/watch?v=test');

      expect(download.id, 'test-id');
      expect(download.status, 'downloading');
    });
  });
}
```

### 4.3 Type Safety Checklist

**Backend (Python):**
- ✅ Pydantic models for all request/response bodies
- ✅ Type hints on all function signatures
- ✅ Mypy strict mode enabled
- ✅ Consistent ApiResponse envelope

**Flutter (Dart):**
- ✅ Strong typing (no `dynamic` unless necessary)
- ✅ Null safety enabled
- ✅ `fromJson` factory constructors
- ✅ Linter rules enforced (`analysis_options.yaml`)

---

## Phase 5: Packaging & Deployment

### 5.1 Backend Bundling (PyInstaller)

```python
# backend/build.py
import PyInstaller.__main__
import sys
import platform

def build_backend():
    args = [
        'main.py',
        '--onefile',
        '--name=mp3yap-backend',
        '--add-data=database:database',
        '--hidden-import=yt_dlp',
        '--hidden-import=uvicorn',
        '--hidden-import=static_ffmpeg',
        '--clean',
    ]

    if platform.system() == 'Darwin':
        args.append('--target-arch=universal2')  # macOS universal binary

    PyInstaller.__main__.run(args)

if __name__ == '__main__':
    build_backend()
```

```bash
# Build script
cd backend
python build.py

# Output: dist/mp3yap-backend (or .exe on Windows)
```

### 5.2 Flutter Build

```bash
# macOS
flutter build macos --release

# Windows
flutter build windows --release

# Linux
flutter build linux --release
```

### 5.3 Bundle Backend with Flutter

**macOS (.app bundle):**
```
MP3Yap.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   ├── mp3yap_flutter        # Flutter executable
│   │   └── mp3yap-backend         # Python backend binary
│   └── Resources/
│       └── ...
```

Update `BackendService._getBackendPath()`:
```dart
Future<String> _getBackendPath() async {
  if (Platform.isMacOS) {
    // In .app bundle
    final execDir = File(Platform.resolvedExecutable).parent.path;
    return '$execDir/mp3yap-backend';
  }
  // ... Windows/Linux paths
}
```

**Windows (installer):**
```
MP3Yap/
├── mp3yap_flutter.exe
├── mp3yap-backend.exe
└── data/
    └── flutter_assets/
```

**Linux (AppImage or .deb):**
```
/usr/lib/mp3yap/
├── mp3yap_flutter
└── mp3yap-backend

/usr/bin/mp3yap -> /usr/lib/mp3yap/mp3yap_flutter
```

### 5.4 Installer Creation

**macOS (DMG):**
```bash
# Use create-dmg
create-dmg \
  --volname "MP3 Yap" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  MP3Yap.dmg \
  build/macos/Build/Products/Release/MP3Yap.app
```

**Windows (Inno Setup):**
```pascal
[Setup]
AppName=MP3 Yap
AppVersion=3.0.0
DefaultDirName={pf}\MP3Yap
OutputBaseFilename=MP3Yap-Setup

[Files]
Source: "build\windows\runner\Release\*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "backend\dist\mp3yap-backend.exe"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\MP3 Yap"; Filename: "{app}\mp3yap_flutter.exe"
```

---

## Phase 6: Migration Checklist

### Pre-Migration
- [ ] Backend API fully tested
- [ ] Flutter screens fully implemented
- [ ] WebSocket progress working
- [ ] All existing features migrated
- [ ] Cross-platform testing complete

### Migration Day
- [ ] Create backup of PyQt5 codebase
- [ ] Move `core/`, `database/`, `utils/` to `backend/`
- [ ] Delete `ui/`, `styles/`, `mp3yap_gui.py`
- [ ] Update `requirements.txt` (backend only)
- [ ] Update README.md with new architecture
- [ ] Create release builds (macOS/Windows/Linux)
- [ ] Test installers on clean machines

### Post-Migration
- [ ] Update documentation
- [ ] Create migration guide for users
- [ ] Monitor for issues
- [ ] Collect user feedback

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│             Flutter Desktop App                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  UI (Material Design 3)                        │  │
│  │  ├─ DownloadScreen                             │  │
│  │  ├─ HistoryScreen                              │  │
│  │  ├─ QueueScreen                                │  │
│  │  └─ SettingsScreen                             │  │
│  └────────────────────────────────────────────────┘  │
│                  ↕                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  Riverpod Providers                            │  │
│  │  ├─ downloadsProvider                          │  │
│  │  ├─ historyProvider                            │  │
│  │  └─ progressStreamProvider (WebSocket)         │  │
│  └────────────────────────────────────────────────┘  │
│                  ↕                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  ApiClient (Dio)                               │  │
│  │  └─ baseUrl: http://127.0.0.1:<port>          │  │
│  └────────────────────────────────────────────────┘  │
│                  ↕                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  BackendService                                │  │
│  │  ├─ Process.start(backend)                     │  │
│  │  ├─ Read stdout → parse port                   │  │
│  │  └─ Configure Dio baseUrl                      │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
                   ↕ HTTP + WebSocket
              (localhost random port)
┌──────────────────────────────────────────────────────┐
│        Python Backend (FastAPI + Uvicorn)            │
│  ┌────────────────────────────────────────────────┐  │
│  │  Startup                                       │  │
│  │  ├─ uvicorn.run(app, host='127.0.0.1', port=0)│  │
│  │  └─ print("BACKEND_READY PORT=<port>")        │  │
│  └────────────────────────────────────────────────┘  │
│                  ↕                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  REST API Routes (JSON)                        │  │
│  │  ├─ POST /api/downloads                        │  │
│  │  ├─ GET  /api/downloads                        │  │
│  │  ├─ GET  /api/history                          │  │
│  │  └─ PATCH /api/config                          │  │
│  └────────────────────────────────────────────────┘  │
│                  ↕                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  WebSocket                                     │  │
│  │  └─ /ws/download/{id}                          │  │
│  └────────────────────────────────────────────────┘  │
│                  ↕                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │  Core Logic (Reused from PyQt5)               │  │
│  │  ├─ Downloader (yt-dlp + FFmpeg)               │  │
│  │  ├─ DatabaseManager (SQLite)                   │  │
│  │  └─ ConfigManager (JSON)                       │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## Risk Assessment

| Risk Level | Description | Mitigation |
|-----------|-------------|------------|
| **Düşük** | Backend logic reuse | ✅ Proven code, wrap in FastAPI |
| **Düşük** | HTTP communication | ✅ Standard protocols, well-tested |
| **Düşük** | Random port conflicts | ✅ OS handles port allocation |
| **Orta** | Backend process management | ⚠️ Test process lifecycle thoroughly |
| **Orta** | Cross-platform packaging | ⚠️ Test on all target platforms |
| **Yüksek** | None | ✅ All technologies are production-ready |

---

## Performance Expectations

### Startup Time
- Backend process start: ~1-2 seconds
- Port discovery (stdout): ~100ms
- Flutter → Backend connection: ~50ms
- **Total**: ~1.5-2 seconds

### Communication Latency
- HTTP request: ~2-5ms (localhost)
- WebSocket message: ~1-3ms
- **Impact**: Negligible (bottleneck is yt-dlp 10-30s + FFmpeg 5-15s)

### Memory Usage
- Backend: ~40-60MB (Python + yt-dlp)
- Flutter: ~80-120MB (Dart VM + Skia)
- **Total**: ~150-200MB (same as PyQt5)

---

## Logging & Debugging

### Backend Logging
```python
# backend/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()  # For Flutter to read
    ]
)

logger = logging.getLogger(__name__)
```

### Flutter Logging
```dart
// Flutter reads backend stdout/stderr
_process!.stdout.transform(utf8.decoder).listen((line) {
  print('[Backend] $line');
  // Can also write to file
});

_process!.stderr.transform(utf8.decoder).listen((line) {
  print('[Backend Error] $line');
});
```

---

## Troubleshooting

### Backend Not Starting
1. Check backend binary exists and is executable
2. Check stdout for errors: `print('[Backend Error]', flush=True)`
3. Try running backend manually: `./mp3yap-backend`

### Port Not Detected
1. Ensure backend prints exactly: `BACKEND_READY PORT=<number>`
2. Check timeout duration (increase if needed)
3. Verify stdout is not buffered (use `flush=True`)

### API Connection Failed
1. Verify port is correct
2. Check firewall settings
3. Test with curl: `curl http://127.0.0.1:<port>/api/health`

---

## Beklenen Sonuç

After migration completion:

- ✅ Modern Flutter UI (Material Design 3)
- ✅ Full cross-platform (macOS/Windows/Linux)
- ✅ Zero port conflicts (OS-managed random port)
- ✅ Simple, pragmatic architecture
- ✅ 80%+ Python code reuse
- ✅ Real-time progress (WebSocket)
- ✅ Easy to debug (standard HTTP tools)
- ✅ Type-safe communication (Pydantic ↔ Dart)
- ✅ Production-ready deployment
- ✅ Better UX with Flutter animations

---

## Notlar

- ✅ **Pragmatic approach**: HTTP + random port (port=0)
- ✅ **No unnecessary complexity**: Standard protocols only
- ✅ **Cross-platform**: Same code for all platforms
- ✅ **Easy debugging**: Standard HTTP tools (Postman, curl)
- ✅ **Production-ready**: All technologies battle-tested
- ⏱️ **Tahmini süre**: 4-6 hafta
- 🎯 **Hedef**: Modern, maintainable, cross-platform desktop app

---

**Plan Oluşturulma Tarihi:** 2025-11-23
**Son Güncelleme:** 2025-11-23 (HTTP + Random Port yaklaşımı)
**Hazırlayan:** Claude (Sonnet 4.5)
**Codebase:** /Users/yerli/Developer/mehmetyerli/mp3yap
