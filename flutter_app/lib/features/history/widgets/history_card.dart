import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/history_item.dart';
import '../../../core/utils/platform_utils.dart';
import '../../../shared/widgets/media_item_card.dart';
import '../../../shared/widgets/play_button.dart';
import '../providers/history_provider.dart';

/// Card widget displaying a single history item
class HistoryCard extends ConsumerWidget {
  final HistoryItem item;

  const HistoryCard({
    super.key,
    required this.item,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return MediaItemCard(
      title: item.videoTitle,
      onTap: () => _showDetailsDialog(context, ref),
      metadata: [
        MediaMetadataItem(
          icon: Icons.access_time,
          text: item.formattedDate,
        ),
        MediaMetadataItem(
          icon: Icons.timer,
          text: item.formattedDuration,
        ),
        MediaMetadataItem(
          icon: Icons.storage,
          text: item.formattedSize,
        ),
      ],
      actions: [
        // Play button (if file exists)
        if (item.filePath != null)
          PlayButton(filePath: item.filePath!),
        // Show in folder button (if file exists)
        if (item.filePath != null)
          IconButton(
            onPressed: () => _showInFolder(context),
            icon: const Icon(Icons.folder_open, size: 20),
            tooltip: 'Show in Folder',
            visualDensity: VisualDensity.compact,
          ),
        // Delete button
        IconButton(
          onPressed: () => _confirmDelete(context, ref),
          icon: const Icon(Icons.delete_outline, size: 20),
          tooltip: 'Delete',
          color: colorScheme.error,
          visualDensity: VisualDensity.compact,
        ),
      ],
    );
  }

  void _showDetailsDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Download Details'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('Title', item.videoTitle),
              if (item.channelName != null)
                _buildLinkRow(
                  context,
                  'Channel',
                  item.channelName!,
                  item.channelUrl,
                ),
              _buildLinkRow(
                context,
                'YouTube',
                'Open Video',
                item.url,
              ),
              _buildDetailRow('File Name', item.fileName),
              if (item.filePath != null)
                _buildDetailRow('File Path', item.filePath!),
              _buildDetailRow('Format', item.format.toUpperCase()),
              _buildDetailRow('Size', item.formattedSize),
              _buildDetailRow('Duration', item.formattedDuration),
              _buildDetailRow('Downloaded', item.formattedDate),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: Colors.black87,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLinkRow(BuildContext context, String label, String text, String? url) {
    final hasUrl = url != null && url.isNotEmpty;
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Expanded(
            child: hasUrl
                ? Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Open link button
                      InkWell(
                        onTap: () => _openUrl(context, url),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              text,
                              style: TextStyle(
                                color: theme.colorScheme.primary,
                                decoration: TextDecoration.underline,
                              ),
                            ),
                            const SizedBox(width: 4),
                            Icon(
                              Icons.open_in_new,
                              size: 14,
                              color: theme.colorScheme.primary,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Copy button
                      InkWell(
                        onTap: () => _copyToClipboard(context, url),
                        borderRadius: BorderRadius.circular(4),
                        child: Padding(
                          padding: const EdgeInsets.all(4),
                          child: Icon(
                            Icons.copy,
                            size: 16,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ],
                  )
                : Text(
                    text,
                    style: const TextStyle(color: Colors.black87),
                  ),
          ),
        ],
      ),
    );
  }

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('URL copied'),
        duration: Duration(seconds: 1),
      ),
    );
  }

  Future<void> _openUrl(BuildContext context, String url) async {
    try {
      await openUrl(url);
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error opening URL: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _showInFolder(BuildContext context) async {
    if (item.filePath == null) return;

    try {
      await openInFolder(item.filePath!);
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

  Future<void> _confirmDelete(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete from History'),
        content: Text('Remove "${item.videoTitle}" from history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final success = await ref.read(historyProvider.notifier).deleteItem(item.id);

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              success
                  ? 'Deleted from history'
                  : 'Failed to delete item',
            ),
            backgroundColor: success ? Colors.green : Colors.red,
          ),
        );
      }
    }
  }
}
