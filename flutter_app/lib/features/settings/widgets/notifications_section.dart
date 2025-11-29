import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart';
import '../../../core/providers/providers.dart';

class NotificationsSection extends ConsumerWidget {
  const NotificationsSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final settings = ref.watch(notificationSettingsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'settings.notifications.title'.tr(),
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        SwitchListTile(
          title: Text('settings.notifications.sound'.tr()),
          subtitle: Text('settings.notifications.sound_subtitle'.tr()),
          secondary: const Icon(Icons.notifications_outlined),
          value: settings.soundEnabled,
          onChanged: (value) {
            ref
                .read(notificationSettingsProvider.notifier)
                .setSoundEnabled(value);
            // Test the sound when enabling
            if (value) {
              ref.read(notificationServiceProvider).playCompletionSound();
            }
          },
        ),
      ],
    );
  }
}
