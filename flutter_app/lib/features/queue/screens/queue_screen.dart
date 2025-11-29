import 'package:flutter/material.dart';
import '../../../shared/widgets/empty_state_widget.dart';

/// Simple Queue Screen placeholder
/// Full queue management can be implemented later if needed
class QueueScreen extends StatelessWidget {
  const QueueScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Download Queue'),
      ),
      body: const EmptyStateWidget(
        icon: Icons.queue_music,
        title: 'Queue Management',
        subtitle: 'Downloads start immediately',
      ),
    );
  }
}
