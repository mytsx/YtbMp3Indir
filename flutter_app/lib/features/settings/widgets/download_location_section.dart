import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:easy_localization/easy_localization.dart';
import '../providers/settings_provider.dart';

class DownloadLocationSection extends ConsumerWidget {
  const DownloadLocationSection({super.key});

  Future<void> _selectFolder(
      BuildContext context, WidgetRef ref, String currentDir) async {
    try {
      final result = await FilePicker.platform.getDirectoryPath(
        dialogTitle: 'settings.download_location.select_dialog_title'.tr(),
        initialDirectory: currentDir.isNotEmpty ? currentDir : null,
      );

      if (result != null) {
        ref.read(settingsProvider.notifier).setDownloadFolder(result);
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('settings.download_location.error_select'
                .tr(args: [e.toString()])),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'settings.download_location.title'.tr(),
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        ListTile(
          leading: const Icon(Icons.folder_outlined),
          title: Text('settings.download_location.label'.tr()),
          subtitle: Text(
            settings.outputDir.isNotEmpty
                ? settings.outputDir
                : 'settings.download_location.not_set'.tr(),
            style: TextStyle(
              color: settings.outputDir.isNotEmpty ? null : Colors.grey,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => _selectFolder(context, ref, settings.outputDir),
        ),
        SwitchListTile(
          secondary: const Icon(Icons.open_in_new),
          title: Text('settings.download_location.auto_open'.tr()),
          subtitle: Text('settings.download_location.auto_open_subtitle'.tr()),
          value: settings.autoOpen,
          onChanged: (value) {
            ref.read(settingsProvider.notifier).updateConfig(autoOpen: value);
          },
        ),
      ],
    );
  }
}
