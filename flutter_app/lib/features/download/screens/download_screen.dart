import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/download_provider.dart';
import '../widgets/download_card.dart';

/// Main download screen
class DownloadScreen extends ConsumerStatefulWidget {
  const DownloadScreen({super.key});

  @override
  ConsumerState<DownloadScreen> createState() => _DownloadScreenState();
}

class _DownloadScreenState extends ConsumerState<DownloadScreen> {
  final TextEditingController _urlController = TextEditingController();
  bool _isDownloading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _startDownload() async {
    final url = _urlController.text.trim();

    if (url.isEmpty) {
      setState(() {
        _errorMessage = 'Please enter a YouTube URL';
      });
      return;
    }

    // Basic URL validation
    if (!url.contains('youtube.com') && !url.contains('youtu.be')) {
      setState(() {
        _errorMessage = 'Please enter a valid YouTube URL';
      });
      return;
    }

    setState(() {
      _isDownloading = true;
      _errorMessage = null;
    });

    try {
      // Call provider to start download
      await ref.read(startDownloadProvider(url).future);

      // Clear URL on success
      _urlController.clear();

      // Show success snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Download started!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to start download: $e';
      });

      // Show error snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isDownloading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Watch downloads list
    final downloads = ref.watch(downloadsProvider);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // URL Input section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // URL TextField
                    TextField(
                      controller: _urlController,
                      decoration: InputDecoration(
                        labelText: 'YouTube URL',
                        hintText: 'https://youtube.com/watch?v=...',
                        prefixIcon: const Icon(Icons.link),
                        border: const OutlineInputBorder(),
                        errorText: _errorMessage,
                      ),
                      maxLines: 1,
                      textInputAction: TextInputAction.done,
                      onSubmitted: (_) => _startDownload(),
                    ),
                    const SizedBox(height: 16),

                    // Download button
                    FilledButton.icon(
                      onPressed: _isDownloading ? null : _startDownload,
                      icon: _isDownloading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.download),
                      label: Text(_isDownloading
                          ? 'Starting...'
                          : 'Start Download'),
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        textStyle: const TextStyle(fontSize: 16),
                      ),
                    ),

                    // Tips
                    const SizedBox(height: 12),
                    Text(
                      'Tip: You can download individual videos or entire playlists',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey.shade600,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Downloads header
            Row(
              children: [
                Text(
                  'Active Downloads',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(width: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${downloads.length}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue.shade900,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Downloads list
            Expanded(
              child: downloads.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.download_outlined,
                            size: 48,
                            color: Colors.grey.shade300,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'No downloads yet',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey.shade600,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Enter a YouTube URL above to get started',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade500,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      itemCount: downloads.length,
                      itemBuilder: (context, index) {
                        final download = downloads[index];
                        return DownloadCard(download: download);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
