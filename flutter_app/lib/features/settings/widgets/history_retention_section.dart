// ignore_for_file: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart';
import '../providers/settings_provider.dart';

class HistoryRetentionSection extends ConsumerWidget {
  const HistoryRetentionSection({super.key});

  Map<int, String> get _retentionOptions => {
        0: 'settings.history_retention.forever'.tr(),
        7: 'settings.history_retention.days_7'.tr(),
        30: 'settings.history_retention.days_30'.tr(),
        90: 'settings.history_retention.days_90'.tr(),
      };

  void _showRetentionDialog(
      BuildContext context, WidgetRef ref, int currentDays) {
    showDialog(
      context: context,
      builder: (context) => SimpleDialog(
        title: Text('settings.history_retention.title'.tr()),
        children: _retentionOptions.entries.map((entry) {
          final days = entry.key;
          final label = entry.value;
          return RadioListTile<int>(
            title: Text(label),
            subtitle: Text(days == 0
                ? 'settings.history_retention.subtitle_forever'.tr()
                : 'settings.history_retention.subtitle_days'
                    .tr(args: [days.toString()])),
            value: days,
            groupValue: currentDays,
            onChanged: (value) {
              Navigator.pop(context);
              if (value != null) {
                ref
                    .read(settingsProvider.notifier)
                    .updateConfig(historyRetentionDays: value);
              }
            },
          );
        }).toList(),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final theme = Theme.of(context);
    final label = _retentionOptions[settings.historyRetentionDays] ??
        '${settings.historyRetentionDays} ${'settings.history_retention.days_suffix'.tr()}';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'settings.history_retention.section_title'.tr(),
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        ListTile(
          leading: const Icon(Icons.history),
          title: Text('settings.history_retention.keep_history_for'.tr()),
          subtitle: Text(label),
          trailing: const Icon(Icons.chevron_right),
          onTap: () =>
              _showRetentionDialog(context, ref, settings.historyRetentionDays),
        ),
      ],
    );
  }
}
