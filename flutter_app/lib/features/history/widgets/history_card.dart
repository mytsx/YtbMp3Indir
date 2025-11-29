import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart';
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
        if (item.filePath != null) PlayButton(filePath: item.filePath!),
        // Show in folder button (if file exists)
        if (item.filePath != null)
          IconButton(
            onPressed: () => _showInFolder(context),
            icon: const Icon(Icons.folder_open, size: 20),
            tooltip: 'card.show_in_folder'.tr(),
            visualDensity: VisualDensity.compact,
          ),
        // Delete button
        IconButton(
          onPressed: () => _confirmDelete(context, ref),
          icon: const Icon(Icons.delete_outline, size: 20),
          tooltip: 'card.delete'.tr(),
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
        title: Text('dialog.download_details'.tr()),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow(
                  context, 'dialog.labels.title'.tr(), item.videoTitle),
              if (item.channelName != null)
                _buildLinkRow(
                  context,
                  'dialog.labels.channel'.tr(),
                  item.channelName!,
                  item.channelUrl,
                ),
              _buildLinkRow(
                context,
                'dialog.labels.youtube'.tr(),
                'card.open_video'.tr(),
                item.url,
              ),
              _buildDetailRow(
                  context, 'dialog.labels.file_name'.tr(), item.fileName),
              if (item.filePath != null)
                _buildDetailRow(
                    context, 'dialog.labels.file_path'.tr(), item.filePath!),
              _buildDetailRow(context, 'dialog.labels.format'.tr(),
                  item.format.toUpperCase()),
              _buildDetailRow(
                  context, 'dialog.labels.size'.tr(), item.formattedSize),
              _buildDetailRow(context, 'dialog.labels.duration'.tr(),
                  item.formattedDuration),
              _buildDetailRow(
                  context, 'dialog.labels.downloaded'.tr(), item.formattedDate),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('dialog.close'.tr()),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(BuildContext context, String label, String value) {
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
            child: Text(
              value,
              style: TextStyle(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLinkRow(
      BuildContext context, String label, String text, String? url) {
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
                    style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
                  ),
          ),
        ],
      ),
    );
  }

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('messages.url_copied'.tr()),
        duration: const Duration(seconds: 1),
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
            content: Text('messages.url_open_error'.tr(args: [e.toString()])),
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
            content:
                Text('messages.folder_open_error'.tr(args: [e.toString()])),
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
        title: Text('dialog.delete_history_title'.tr()),
        content: Text(
            'dialog.delete_history_confirm'.tr(args: [item.videoTitle])),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text('dialog.cancel'.tr()),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: Text('dialog.delete'.tr()),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final success =
          await ref.read(historyProvider.notifier).deleteItem(item.id);

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              success
                  ? 'messages.history_deleted'.tr()
                  : 'messages.history_delete_failed'.tr(),
            ),
            backgroundColor: success ? Colors.green : Colors.red,
          ),
        );
      }
    }
  }
}
