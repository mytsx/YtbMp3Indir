import 'package:flutter/material.dart';
import '../core/services/backend_service.dart';
import '../core/api/api_client.dart';

/// Simple demo screen showing backend integration
/// Demonstrates:
/// 1. Starting backend and discovering port
/// 2. Making HTTP requests to backend
/// 3. Displaying responses
class DemoScreen extends StatefulWidget {
  const DemoScreen({super.key});

  @override
  State<DemoScreen> createState() => _DemoScreenState();
}

class _DemoScreenState extends State<DemoScreen> {
  final BackendService _backendService = BackendService();
  ApiClient? _apiClient;

  final TextEditingController _urlController = TextEditingController();

  String _status = 'Not started';
  String? _response;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _startBackend();
  }

  @override
  void dispose() {
    _backendService.stop();
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _startBackend() async {
    setState(() {
      _status = 'Starting backend...';
    });

    try {
      await _backendService.start();

      // Create API client with discovered port
      _apiClient = ApiClient(_backendService.port!);

      // Test health check
      final health = await _apiClient!.healthCheck();

      setState(() {
        _status = 'Backend ready on port ${_backendService.port}';
        _response = 'Health check: ${health.toString()}';
      });
    } catch (e) {
      setState(() {
        _status = 'Failed to start backend: $e';
      });
    }
  }

  Future<void> _testDownload() async {
    if (_apiClient == null) {
      setState(() {
        _response = 'Backend not ready';
      });
      return;
    }

    if (_urlController.text.isEmpty) {
      setState(() {
        _response = 'Please enter a URL';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _response = null;
    });

    try {
      final result = await _apiClient!.startDownload(_urlController.text);

      setState(() {
        _response = '''
✅ Download Started!

ID: ${result['id']}
URL: ${result['url']}
Status: ${result['status']}
Progress: ${result['progress']}%
''';
      });
    } catch (e) {
      setState(() {
        _response = '❌ Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _testConfig() async {
    if (_apiClient == null) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final config = await _apiClient!.getConfig();

      setState(() {
        _response = '''
⚙️ Configuration:

Output Dir: ${config['output_dir']}
Quality: ${config['quality']} kbps
Auto Open: ${config['auto_open']}
Language: ${config['language']}
''';
      });
    } catch (e) {
      setState(() {
        _response = '❌ Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MP3Yap Backend Demo'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Card
            Card(
              color: _backendService.isRunning
                  ? Colors.green.shade50
                  : Colors.orange.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Backend Status',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _status,
                      style: TextStyle(
                        fontSize: 14,
                        color: _backendService.isRunning
                            ? Colors.green.shade900
                            : Colors.orange.shade900,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // URL Input
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'YouTube URL',
                hintText: 'https://youtube.com/watch?v=...',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.link),
              ),
            ),
            const SizedBox(height: 16),

            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _testDownload,
                    icon: _isLoading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.download),
                    label: Text(_isLoading ? 'Loading...' : 'Test Download'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _isLoading ? null : _testConfig,
                    icon: const Icon(Icons.settings),
                    label: const Text('Get Config'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
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
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ),
                ),
              ),

            // Instructions
            if (_response == null)
              const Expanded(
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Instructions',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 12),
                        Text('1. Backend starts automatically'),
                        Text('2. Enter a YouTube URL'),
                        Text('3. Click "Test Download" to start'),
                        Text('4. Or click "Get Config" to view settings'),
                        SizedBox(height: 12),
                        Text(
                          'This demo shows:',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text('✓ Backend process management'),
                        Text('✓ Dynamic port discovery'),
                        Text('✓ HTTP API communication'),
                        Text('✓ Standardized response handling'),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
