import 'package:flutter/material.dart';
import 'package:easy_localization/easy_localization.dart';
import '../../../shared/widgets/empty_state_widget.dart';

/// Simple Queue Screen placeholder
/// Full queue management can be implemented later if needed
class QueueScreen extends StatelessWidget {
  const QueueScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('queue.title'.tr()),
      ),
      body: EmptyStateWidget(
        icon: Icons.queue_music,
        title: 'queue.empty_title'.tr(),
        subtitle: 'queue.empty_subtitle'.tr(),
      ),
    );
  }
}
