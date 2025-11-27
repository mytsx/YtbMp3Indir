import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/conversion.dart';
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

    // Get latest conversion state from provider (updated by WebSocket)
    final conversions = ref.watch(conversionsProvider);
    final latestConversion = conversions.firstWhere(
      (c) => c.id == conversion.id,
      orElse: () => conversion,
    );

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
                _getStatusIcon(latestConversion.status),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        latestConversion.fileName,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _getStatusText(latestConversion.status),
                        style: TextStyle(
                          fontSize: 13,
                          color: _getStatusColor(latestConversion.status),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            if (latestConversion.isActive) ...[
              const SizedBox(height: 16),

              // Progress bar
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: latestConversion.progress / 100,
                  minHeight: 8,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: const AlwaysStoppedAnimation<Color>(Colors.orange),
                ),
              ),

              const SizedBox(height: 8),

              // Progress details
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${latestConversion.progress}%',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (latestConversion.duration != null)
                    Text(
                      'Duration: ${_formatDuration(latestConversion.duration!)}',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey.shade600,
                      ),
                    ),
                ],
              ),
            ],

            if (latestConversion.isCompleted) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.green, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Saved to: ${latestConversion.outputPath ?? 'Unknown'}',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey.shade700,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],

            if (latestConversion.isFailed) ...[
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
                        latestConversion.error ?? 'Unknown error',
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
      case 'converting':
        return const SizedBox(
          width: 32,
          height: 32,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case 'completed':
        return const Icon(Icons.check_circle, color: Colors.green, size: 32);
      case 'failed':
        return const Icon(Icons.error, color: Colors.red, size: 32);
      case 'cancelled':
        return const Icon(Icons.cancel, color: Colors.grey, size: 32);
      default:
        return const Icon(Icons.transform, color: Colors.orange, size: 32);
    }
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'pending':
        return 'Pending...';
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
      case 'converting':
        return Colors.orange;
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'cancelled':
        return Colors.grey;
      default:
        return Colors.blue;
    }
  }

  String _formatDuration(double seconds) {
    final duration = Duration(seconds: seconds.toInt());
    final minutes = duration.inMinutes;
    final secs = duration.inSeconds % 60;
    return '${minutes}m ${secs}s';
  }
}
