import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/download.dart';
import '../../../core/utils/platform_utils.dart';
import '../../../shared/widgets/media_item_card.dart';
import '../../../shared/widgets/play_button.dart';
import '../providers/download_provider.dart';

/// Download card showing progress and status
class DownloadCard extends ConsumerWidget {
  final Download download;

  const DownloadCard({
    super.key,
    required this.download,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch WebSocket progress updates to trigger rebuilds
    ref.watch(downloadProgressProvider(download.id));

    // Get latest download state from provider (updated by WebSocket)
    final downloads = ref.watch(downloadsProvider);
    final latestDownload = downloads.firstWhere(
      (d) => d.id == download.id,
      orElse: () => download,
    );

    // Completed state - HistoryCard style layout
    if (latestDownload.isCompleted) {
      return MediaItemCard(
        title: latestDownload.videoTitle ?? 'Download completed',
        actions: [
          if (latestDownload.filePath != null)
            PlayButton(filePath: latestDownload.filePath!),
          if (latestDownload.filePath != null)
            IconButton(
              onPressed: () => _showInFolder(context, latestDownload.filePath!),
              icon: const Icon(Icons.folder_open, size: 20),
              tooltip: 'Show in Folder',
              visualDensity: VisualDensity.compact,
            ),
        ],
      );
    }

    // Active/Failed state - progress card
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title row
            Row(
              children: [
                _getStatusIcon(latestDownload.status),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        latestDownload.videoTitle ?? 'Fetching info...',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _getStatusText(latestDownload.status),
                        style: TextStyle(
                          fontSize: 13,
                          color: _getStatusColor(latestDownload.status),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            if (latestDownload.isActive) ...[
              const SizedBox(height: 16),

              // Progress bar
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: latestDownload.progress / 100,
                  minHeight: 8,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getProgressColor(latestDownload.status),
                  ),
                ),
              ),

              const SizedBox(height: 8),

              // Progress details
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${latestDownload.progress}%',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (latestDownload.speed != null || latestDownload.eta != null)
                    Text(
                      [
                        if (latestDownload.speed != null) latestDownload.speed!,
                        if (latestDownload.eta != null) 'ETA: ${latestDownload.eta!}',
                      ].join(' • '),
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey.shade600,
                      ),
                    ),
                ],
              ),
            ],

            if (latestDownload.isFailed) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        latestDownload.error ?? 'Unknown error',
                        style: const TextStyle(
                          fontSize: 13,
                          color: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _getStatusIcon(String status) {
    switch (status) {
      case 'downloading':
        return const CircularProgressIndicator(strokeWidth: 2);
      case 'converting':
        return const CircularProgressIndicator(strokeWidth: 2);
      case 'completed':
        return const Icon(Icons.check_circle, color: Colors.green, size: 32);
      case 'failed':
        return const Icon(Icons.error, color: Colors.red, size: 32);
      case 'cancelled':
        return const Icon(Icons.cancel, color: Colors.grey, size: 32);
      default:
        return const Icon(Icons.downloading, color: Colors.blue, size: 32);
    }
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'pending':
        return 'Pending...';
      case 'downloading':
        return 'Downloading...';
      case 'converting':
        return 'Converting to MP3...';
      case 'completed':
        return 'Completed!';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'downloading':
      case 'converting':
        return Colors.blue;
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'cancelled':
        return Colors.grey;
      default:
        return Colors.orange;
    }
  }

  Color _getProgressColor(String status) {
    if (status == 'converting') {
      return Colors.orange;
    }
    return Colors.blue;
  }

  Future<void> _showInFolder(BuildContext context, String filePath) async {
    try {
      await openInFolder(filePath);
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not open folder: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
