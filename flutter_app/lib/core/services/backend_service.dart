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
    // First check if backend is already running (user started it manually)
    print('Checking if backend is already running on port $_fixedPort...');
    if (await healthCheck()) {
      print('✅ Backend already running on port $_fixedPort (externally started)');
      return;
    }

    if (isRunning) {
      print('Backend process already managed by this service');
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
