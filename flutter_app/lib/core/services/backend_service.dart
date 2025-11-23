import 'dart:async';
import 'dart:convert';
import 'dart:io';

/// Manages the Python backend process lifecycle
/// Uses TTS-proven pattern: dynamic port via .backend_port file
class BackendService {
  Process? _process;
  int? _port;  // Dynamic port from .backend_port file

  int get port => _port ?? 8000;  // Fallback to 8000
  bool get isRunning => _process != null;

  /// Start the backend process (TTS-proven pattern)
  Future<void> start() async {
    if (isRunning) {
      print('Backend process already managed by this service');
      return;
    }

    // Check if backend is already running (TTS pattern - auto-detect)
    print('🔍 Checking if backend is already running...');

    // Try to read existing port file
    try {
      final projectRoot = await _getProjectRoot();
      final portFile = File('$projectRoot/.backend_port');

      if (await portFile.exists()) {
        final content = await portFile.readAsString();
        _port = int.parse(content.trim());
        print('Found .backend_port file with port: $_port');

        // Test if backend is actually responsive
        if (await healthCheck()) {
          print('✅ Backend already running and healthy on port: $_port');
          return;
        } else {
          print('Port file exists but backend not responsive, will restart...');
          await portFile.delete();
        }
      }
    } catch (e) {
      print('No existing backend detected: $e');
    }

    print('🚀 Starting backend with TTS-proven pattern...');

    try {
      // Get project root
      final projectRoot = await _getProjectRoot();
      final backendDir = '$projectRoot/backend';

      print('Project root: $projectRoot');
      print('Backend directory: $backendDir');

      // Check if backend directory exists
      if (!await Directory(backendDir).exists()) {
        throw Exception('Backend directory not found at: $backendDir');
      }

      // DELETE stale .backend_port file (TTS pattern)
      final portFile = File('$projectRoot/.backend_port');
      if (await portFile.exists()) {
        await portFile.delete();
        print('Deleted stale .backend_port file');
      }

      // Start Python backend (TTS pattern: use venv python)
      // CRITICAL: Set PYTHONUNBUFFERED=1 for real-time logging
      final venvPython = '$projectRoot/.venv/bin/python';

      // Check if venv exists, fallback to system python3
      final pythonExecutable = await File(venvPython).exists()
          ? venvPython
          : 'python3';

      print('Using Python: $pythonExecutable');

      _process = await Process.start(
        pythonExecutable,
        ['main.py'],
        workingDirectory: backendDir,
        runInShell: true,
        environment: {
          'PYTHONUNBUFFERED': '1',  // Force unbuffered output (TTS pattern)
        },
      );

      // Capture stdout for logging
      _process!.stdout
          .transform(utf8.decoder)
          .transform(LineSplitter())
          .listen((line) {
        print('[Backend] $line');
      });

      // Capture stderr for error logging
      _process!.stderr
          .transform(utf8.decoder)
          .transform(LineSplitter())
          .listen((line) {
        print('[Backend ERROR] $line');
      });

      // Monitor process exit
      _process!.exitCode.then((code) {
        print('Backend process exited with code: $code');
        _process = null;
        _port = null;
      });

      // READ dynamic port from .backend_port file (TTS pattern - 30s timeout)
      final portRead = await _readBackendPort(projectRoot);
      if (!portRead) {
        throw Exception('Failed to read backend port from .backend_port file');
      }

      print('✅ Backend port discovered: $_port');

      // WAIT for /health endpoint (TTS pattern - 90s timeout for model loading)
      final healthy = await _waitForBackend();
      if (healthy) {
        print('✅ Backend successfully started and healthy on port: $_port');
      } else {
        throw Exception('Backend started but health check failed after 90s');
      }
    } catch (e) {
      print('❌ Failed to start backend: $e');
      await stop();
      rethrow;
    }
  }

  /// Read backend port from .backend_port file (TTS pattern - 30s timeout)
  Future<bool> _readBackendPort(String projectRoot) async {
    final portFile = File('$projectRoot/.backend_port');

    for (int i = 0; i < 30; i++) {  // 30 seconds max
      await Future.delayed(const Duration(seconds: 1));

      if (await portFile.exists()) {
        try {
          final content = await portFile.readAsString();
          _port = int.parse(content.trim());
          print('Read port from .backend_port: $_port');
          return true;
        } catch (e) {
          print('Error reading port file: $e');
        }
      }
    }

    print('⚠️ Timeout: .backend_port file not found after 30 seconds');
    return false;
  }

  /// Get project root directory (parent of flutter_app)
  Future<String> _getProjectRoot() async {
    // Check if PROJECT_ROOT is set (for development)
    final envProjectRoot = Platform.environment['PROJECT_ROOT'];
    if (envProjectRoot != null && envProjectRoot.isNotEmpty) {
      final dir = Directory(envProjectRoot);
      if (await dir.exists()) {
        return envProjectRoot;
      }
    }

    // Try to get from resolved executable path
    // This works when running from flutter run command
    final resolvedPath = Platform.resolvedExecutable;
    var current = File(resolvedPath).parent;

    // Navigate up to find backend directory (max 10 levels)
    for (var i = 0; i < 10; i++) {
      final backendDir = Directory('${current.path}/backend');
      if (await backendDir.exists()) {
        return current.path;
      }
      if (current.path == '/' || current.path == current.parent.path) break;
      current = current.parent;
    }

    // Fallback: Assume we're in flutter_app and go one level up
    // This works when running from IDE or flutter run
    try {
      final flutterAppPath = Platform.script.path;
      if (flutterAppPath.contains('flutter_app')) {
        final parts = flutterAppPath.split('flutter_app');
        if (parts.isNotEmpty) {
          final projectRoot = parts[0].replaceAll(RegExp(r'/+$'), '');
          return projectRoot;
        }
      }
    } catch (e) {
      // Ignore errors from Platform.script in sandbox
    }

    throw Exception('Could not find project root. Set PROJECT_ROOT environment variable.');
  }

  /// Stop the backend process
  Future<void> stop() async {
    if (_process != null) {
      print('Stopping backend...');

      // Try graceful shutdown first
      _process!.kill(ProcessSignal.sigterm);

      // Wait for process to exit (with timeout)
      try {
        await _process!.exitCode.timeout(
          const Duration(seconds: 5),
          onTimeout: () {
            print('Backend did not stop gracefully, force killing...');
            _process!.kill(ProcessSignal.sigkill);
            return -1;
          },
        );
      } catch (e) {
        print('Error stopping backend: $e');
      }

      _process = null;
      print('Backend stopped');
    }
  }

  /// Wait for backend to become healthy (TTS pattern - 90s timeout for model loading)
  Future<bool> _waitForBackend() async {
    for (int i = 0; i < 90; i++) {  // 90 seconds max
      await Future.delayed(const Duration(seconds: 1));

      if (await healthCheck()) {
        return true;
      }

      if (i % 10 == 0 && i > 0) {
        print('Still waiting for backend health check... ${i}s elapsed');
      }
    }

    print('⚠️ Timeout: Backend health check failed after 90 seconds');
    return false;
  }

  /// Check if backend is healthy
  Future<bool> healthCheck() async {
    try {
      final httpClient = HttpClient();
      final request = await httpClient.get('127.0.0.1', port, '/api/config');
      final response = await request.close();

      final success = response.statusCode == 200;
      await response.drain();
      return success;
    } catch (e) {
      // Don't log every failed attempt during startup polling
      return false;
    }
  }
}
