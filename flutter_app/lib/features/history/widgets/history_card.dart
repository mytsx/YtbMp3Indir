import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:audioplayers/audioplayers.dart';
import '../../../core/models/history_item.dart';
import '../../../core/utils/platform_utils.dart';
import '../providers/history_provider.dart';
import '../../player/audio_player_provider.dart';

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

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: () => _showDetailsDialog(context, ref),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            children: [
              // Left side: Title and metadata
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title row
                    Row(
                      children: [
                        Icon(
                          Icons.music_note,
                          color: colorScheme.primary,
                          size: 18,
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            item.videoTitle,
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    // Metadata row
                    Wrap(
                      spacing: 12,
                      runSpacing: 4,
                      children: [
                        _buildMetadata(
                          icon: Icons.access_time,
                          text: item.formattedDate,
                          color: colorScheme.onSurfaceVariant,
                        ),
                        _buildMetadata(
                          icon: Icons.timer,
                          text: item.formattedDuration,
                          color: colorScheme.onSurfaceVariant,
                        ),
                        _buildMetadata(
                          icon: Icons.storage,
                          text: item.formattedSize,
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Right side: Action buttons
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Play button (if file exists)
                  if (item.filePath != null)
                    _buildPlayButton(context, ref, colorScheme),
                  // Show in folder button (if file exists)
                  if (item.filePath != null)
                    IconButton(
                      onPressed: () => _showInFolder(context),
                      icon: const Icon(Icons.folder_open, size: 20),
                      tooltip: 'Klasörde Göster',
                      visualDensity: VisualDensity.compact,
                    ),
                  // Delete button
                  IconButton(
                    onPressed: () => _confirmDelete(context, ref),
                    icon: const Icon(Icons.delete_outline, size: 20),
                    tooltip: 'Sil',
                    color: colorScheme.error,
                    visualDensity: VisualDensity.compact,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetadata({
    required IconData icon,
    required String text,
    required Color color,
  }) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(
            fontSize: 12,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildPlayButton(BuildContext context, WidgetRef ref, ColorScheme colorScheme) {
    final player = ref.watch(audioPlayerProvider);
    final currentlyPlaying = ref.watch(currentlyPlayingProvider);
    final playerStateAsync = ref.watch(playerStateProvider);

    final isThisPlaying = currentlyPlaying == item.filePath;
    final isPlaying = playerStateAsync.value == PlayerState.playing && isThisPlaying;

    return IconButton(
      icon: Icon(
        isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled,
        size: 28,
      ),
      color: colorScheme.primary,
      onPressed: () async {
        if (item.filePath == null) return;

        if (isThisPlaying && isPlaying) {
          // Pause
          await player.pause();
        } else if (isThisPlaying) {
          // Resume
          await player.resume();
        } else {
          // Play new file - ensure absolute path (TTS pattern)
          String filePath = item.filePath!;

          // Convert relative paths to absolute (for legacy database entries)
          if (!filePath.startsWith('/')) {
            // Relative path detected - make it absolute
            final file = File(filePath);
            filePath = file.absolute.path;
            print('Converted relative path to absolute: $filePath');
          }

          // Verify file exists before playing
          if (!await File(filePath).exists()) {
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('File not found: ${File(filePath).path}'),
                  backgroundColor: Colors.red,
                ),
              );
            }
            return;
          }

          await player.stop();
          await player.play(DeviceFileSource(filePath));
          ref.read(currentlyPlayingProvider.notifier).state = filePath;
        }
      },
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
                ? InkWell(
                    onTap: () => _openUrl(context, url),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Flexible(
                          child: Text(
                            text,
                            style: TextStyle(
                              color: theme.colorScheme.primary,
                              decoration: TextDecoration.underline,
                            ),
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
            content: Text('Klasör açılamadı: $e'),
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
