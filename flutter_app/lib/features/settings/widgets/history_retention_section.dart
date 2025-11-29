// ignore_for_file: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/settings_provider.dart';

class HistoryRetentionSection extends ConsumerWidget {
  const HistoryRetentionSection({super.key});

  static const _retentionOptions = {
    0: 'Forever',
    7: '7 days',
    30: '30 days',
    90: '90 days',
  };

  void _showRetentionDialog(
      BuildContext context, WidgetRef ref, int currentDays) {
    showDialog(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('History Retention'),
        children: _retentionOptions.entries.map((entry) {
          final days = entry.key;
          final label = entry.value;
          return RadioListTile<int>(
            title: Text(label),
            subtitle: Text(days == 0
                ? 'Keep all history'
                : 'Delete history older than $days days'),
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
        '${settings.historyRetentionDays} days';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'History',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        ListTile(
          leading: const Icon(Icons.history),
          title: const Text('Keep History For'),
          subtitle: Text(label),
          trailing: const Icon(Icons.chevron_right),
          onTap: () =>
              _showRetentionDialog(context, ref, settings.historyRetentionDays),
        ),
      ],
    );
  }
}
