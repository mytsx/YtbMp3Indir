// ignore_for_file: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/settings_provider.dart';

class AudioQualitySection extends ConsumerWidget {
  const AudioQualitySection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final notifier = ref.read(settingsProvider.notifier);
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'Audio Quality',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        _buildRadioTile(
          title: '128 kbps (Smaller file size)',
          value: '128',
          groupValue: settings.quality,
          onChanged: (val) => notifier.updateConfig(quality: val),
        ),
        _buildRadioTile(
          title: '192 kbps (Recommended)',
          value: '192',
          groupValue: settings.quality,
          onChanged: (val) => notifier.updateConfig(quality: val),
        ),
        _buildRadioTile(
          title: '256 kbps (High quality)',
          value: '256',
          groupValue: settings.quality,
          onChanged: (val) => notifier.updateConfig(quality: val),
        ),
        _buildRadioTile(
          title: '320 kbps (Best quality)',
          value: '320',
          groupValue: settings.quality,
          onChanged: (val) => notifier.updateConfig(quality: val),
        ),
      ],
    );
  }

  Widget _buildRadioTile({
    required String title,
    required String value,
    required String groupValue,
    required ValueChanged<String?> onChanged,
  }) {
    return RadioListTile<String>(
      title: Text(title),
      value: value,
      groupValue: groupValue,
      onChanged: onChanged,
    );
  }
}
