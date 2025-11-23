import 'dart:async';
import 'dart:convert';
import 'dart:io';

/// Manages the Python backend process lifecycle
/// Starts the backend with port=0 and discovers the port from stdout
class BackendService {
  Process? _process;
  int? _port;

  int? get port => _port;
  bool get isRunning => _process != null && _port != null;

  /// Start the backend process and discover port from stdout
  Future<void> start() async {
    if (isRunning) {
      print('Backend already running on port: $_port');
      return;
    }

    final backendPath = await _getBackendPath();
    print('Starting backend: $backendPath');

    // Start backend process
    _process = await Process.start(
      backendPath,
      [], // Backend will choose its own random port
      runInShell: false,
    );

    // Listen to stdout for port discovery
    final portCompleter = Completer<int>();

    // Read stdout line by line
    _process!.stdout
        .transform(utf8.decoder)
        .transform(LineSplitter())
        .listen((line) {
      print('[Backend stdout] $line');

      // Parse "BACKEND_READY PORT=12345"
      if (line.startsWith('BACKEND_READY PORT=')) {
        final portStr = line.split('=')[1].trim();
        final port = int.tryParse(portStr);
        if (port != null && !portCompleter.isCompleted) {
          print('✅ Backend port discovered: $port');
          portCompleter.complete(port);
        }
      }
    });

    // Read stderr for error logging
    _process!.stderr
        .transform(utf8.decoder)
        .transform(LineSplitter())
        .listen((line) {
      print('[Backend stderr] $line');
    });

    // Monitor process exit
    _process!.exitCode.then((code) {
      print('Backend process exited with code: $code');
      _port = null;
      _process = null;
    });

    // Wait for port (timeout: 10 seconds)
    try {
      _port = await portCompleter.future.timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Backend did not report port within 10 seconds');
        },
      );
      print('Backend successfully started on port: $_port');
    } catch (e) {
      print('Failed to start backend: $e');
      await stop();
      rethrow;
    }
  }

  /// Get backend executable path (platform-specific)
  Future<String> _getBackendPath() async {
    // For development: Use Python script directly
    if (Platform.environment.containsKey('FLUTTER_DEV')) {
      // In development, run the Python script directly
      // Make sure to set FLUTTER_DEV=1 environment variable
      return 'python3';
      // Note: You'll need to modify Process.start to pass ['main.py'] as arguments
    }

    // For production: Use bundled binary
    if (Platform.isMacOS) {
      // In .app bundle: Contents/MacOS/mp3yap-backend
      final execDir = File(Platform.resolvedExecutable).parent.path;
      return '$execDir/mp3yap-backend';
    } else if (Platform.isWindows) {
      return 'mp3yap-backend.exe';
    } else {
      // Linux
      return './mp3yap-backend';
    }
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
    if (!isRunning) return false;

    try {
      final httpClient = HttpClient();
      final request = await httpClient.get('127.0.0.1', _port!, '/api/health');
      final response = await request.close();

      if (response.statusCode == 200) {
        final body = await response.transform(utf8.decoder).join();
        print('Health check response: $body');
        return true;
      }
      return false;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }
}
