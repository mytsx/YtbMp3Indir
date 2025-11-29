import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart';
import '../../../core/models/conversion.dart';
import '../../../core/utils/platform_utils.dart';
import '../../../shared/widgets/media_item_card.dart';
import '../../../shared/widgets/play_button.dart';
import '../providers/conversion_provider.dart';

/// Conversion card showing progress and status
class ConversionCard extends ConsumerWidget {
  final Conversion conversion;

  const ConversionCard({
    super.key,
    required this.conversion,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch WebSocket progress updates to trigger rebuilds
    ref.watch(conversionProgressProvider(conversion.id));

    // Get latest conversion state from provider
    final conversions = ref.watch(conversionsProvider);
    final latestConversion = conversions.firstWhere(
      (c) => c.id == conversion.id,
      orElse: () => conversion,
    );

    // Completed: Use simplified MediaItemCard style
    if (latestConversion.isCompleted) {
      return MediaItemCard(
        title: latestConversion.fileName,
        leadingIcon: Icons.check_circle,
        leadingIconColor: Colors.green,
        actions: [
          if (latestConversion.outputPath != null) ...[
            PlayButton(filePath: latestConversion.outputPath!),
            IconButton(
              onPressed: () =>
                  _showInFolder(context, latestConversion.outputPath!),
              icon: const Icon(Icons.folder_open, size: 20),
              tooltip: 'card.show_in_folder'.tr(),
              visualDensity: VisualDensity.compact,
            ),
          ],
        ],
      );
    }

    // Active or Failed: Show progress/error card
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Title row with status
            Row(
              children: [
                _buildStatusIcon(latestConversion.status),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    latestConversion.fileName,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),

            // Progress bar for active conversions
            if (latestConversion.isActive) ...[
              const SizedBox(height: 10),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: latestConversion.progress / 100,
                  minHeight: 6,
                  backgroundColor: Colors.grey.shade200,
                  valueColor:
                      const AlwaysStoppedAnimation<Color>(Colors.orange),
                ),
              ),
              const SizedBox(height: 6),
              Text(
                '${latestConversion.progress}% - ${'card.converting_progress'.tr()}',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
            ],

            // Error message for failed conversions
            if (latestConversion.isFailed) ...[
              const SizedBox(height: 8),
              Text(
                latestConversion.error ?? 'messages.conversion_failed'.tr(),
                style: const TextStyle(fontSize: 12, color: Colors.red),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIcon(String status) {
    switch (status) {
      case 'converting':
        return const SizedBox(
          width: 20,
          height: 20,
          child:
              CircularProgressIndicator(strokeWidth: 2, color: Colors.orange),
        );
      case 'failed':
        return const Icon(Icons.error, color: Colors.red, size: 20);
      case 'cancelled':
        return const Icon(Icons.cancel, color: Colors.grey, size: 20);
      default:
        return const Icon(Icons.transform, color: Colors.orange, size: 20);
    }
  }

  void _showInFolder(BuildContext context, String filePath) async {
    try {
      await openInFolder(filePath);
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
}
