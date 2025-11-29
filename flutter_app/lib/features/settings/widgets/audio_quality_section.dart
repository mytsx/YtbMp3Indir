// ignore_for_file: deprecated_member_use
import 'package:easy_localization/easy_localization.dart';
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

    final Map<String, String> qualityOptions = {
      '128': 'settings.audio_quality.options.128'.tr(),
      '192': 'settings.audio_quality.options.192'.tr(),
      '256': 'settings.audio_quality.options.256'.tr(),
      '320': 'settings.audio_quality.options.320'.tr(),
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'settings.audio_quality.title'.tr(),
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              border: Border.all(color: theme.dividerColor),
              borderRadius: BorderRadius.circular(8),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: settings.quality,
                isExpanded: true,
                icon: const Icon(Icons.arrow_drop_down),
                items: qualityOptions.entries.map((entry) {
                  return DropdownMenuItem<String>(
                    value: entry.key,
                    child: Text(entry.value),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    notifier.updateConfig(quality: newValue);
                  }
                },
              ),
            ),
          ),
        ),
      ],
    );
  }
}
