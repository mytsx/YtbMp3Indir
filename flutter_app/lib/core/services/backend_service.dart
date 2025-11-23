import 'dart:async';
import 'dart:convert';
import 'dart:io';

/// Manages the Python backend process lifecycle
/// For development: Starts uvicorn on fixed port 8000
/// For production: Will use bundled executable
class BackendService {
  Process? _process;
  final int _fixedPort = 8000; // Development fixed port

  int get port => _fixedPort;
  bool get isRunning => _process != null;

  /// Start the backend process
  Future<void> start() async {
    if (isRunning) {
      print('Backend already running on port: $_fixedPort');
      return;
    }

    print('Starting backend on port $_fixedPort...');

    try {
      // Get project root (assuming flutter_app is sibling to backend)
      final projectRoot = await _getProjectRoot();
      final backendDir = '$projectRoot/backend';

      print('Backend directory: $backendDir');

      // Check if backend directory exists
      if (!await Directory(backendDir).exists()) {
        throw Exception('Backend directory not found at: $backendDir');
      }

      // Start uvicorn with fixed port
      _process = await Process.start(
        'uvicorn',
        ['main:app', '--port', '$_fixedPort'],
        workingDirectory: backendDir,
        runInShell: true,
      );

      // Read stdout for logging
      _process!.stdout
          .transform(utf8.decoder)
          .transform(LineSplitter())
          .listen((line) {
        print('[Backend] $line');
      });

      // Read stderr for error logging
      _process!.stderr
          .transform(utf8.decoder)
          .transform(LineSplitter())
          .listen((line) {
        print('[Backend Error] $line');
      });

      // Monitor process exit
      _process!.exitCode.then((code) {
        print('Backend process exited with code: $code');
        _process = null;
      });

      // Wait a bit for backend to start
      await Future.delayed(const Duration(seconds: 2));

      // Verify backend is running
      final healthy = await healthCheck();
      if (healthy) {
        print('✅ Backend successfully started on port: $_fixedPort');
      } else {
        print('⚠️ Backend started but health check failed');
      }
    } catch (e) {
      print('Failed to start backend: $e');
      await stop();
      rethrow;
    }
  }

  /// Get project root directory (parent of flutter_app)
  Future<String> _getProjectRoot() async {
    // In development: flutter_app is in project root
    // Get current working directory and go up one level if we're in flutter_app
    final currentDir = Directory.current.path;

    if (currentDir.endsWith('flutter_app')) {
      return Directory(currentDir).parent.path;
    }

    // Otherwise assume we're already in project root
    return currentDir;
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
      _port = null;
      print('Backend stopped');
    }
  }

  /// Check if backend is healthy
  Future<bool> healthCheck() async {
    try {
      final httpClient = HttpClient();
      final request = await httpClient.get('127.0.0.1', _fixedPort, '/api/config');
      final response = await request.close();

      final success = response.statusCode == 200;
      await response.drain();
      return success;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }
}
