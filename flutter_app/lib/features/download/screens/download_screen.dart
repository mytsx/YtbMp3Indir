import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/cyberpunk_colors.dart';
import '../../../core/providers/providers.dart';
import '../../../shared/widgets/empty_state_widget.dart';
import '../providers/download_provider.dart';
import '../widgets/download_card.dart';
import '../widgets/url_input_card.dart';

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
            backgroundColor: CyberpunkColors.matrixGreen,
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
            backgroundColor: CyberpunkColors.neonPinkGlow,
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

    final themeStyle = ref.watch(themeStyleProvider);
    final isCyberpunk = themeStyle == 'cyberpunk';
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: (isCyberpunk && isDarkMode) ? Colors.transparent : null,
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // URL Input section
            UrlInputCard(
              controller: _urlController,
              isDownloading: _isDownloading,
              errorMessage: _errorMessage,
              onDownloadPressed: _startDownload,
            ),

            const SizedBox(height: 24),

            // Downloads header
            Row(
              children: [
                Text(
                  'Downloads',
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
                    color: isCyberpunk
                        ? CyberpunkColors.neonCyan.withValues(alpha: 0.2)
                        : colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                    border: isCyberpunk
                        ? Border.all(
                            color: CyberpunkColors.neonCyan.withValues(alpha: 0.5),
                            width: 1,
                          )
                        : null,
                  ),
                  child: Text(
                    '${downloads.length}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isCyberpunk
                          ? CyberpunkColors.neonCyan
                          : colorScheme.onPrimaryContainer,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Downloads list
            Expanded(
              child: downloads.isEmpty
                  ? const EmptyStateWidget(
                      icon: Icons.download_outlined,
                      title: 'No downloads yet',
                      subtitle: 'Enter a YouTube URL above to get started',
                      iconSize: 48,
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
