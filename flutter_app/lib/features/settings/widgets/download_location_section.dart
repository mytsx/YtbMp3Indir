import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../providers/settings_provider.dart';

class DownloadLocationSection extends ConsumerWidget {
  const DownloadLocationSection({super.key});

  Future<void> _selectFolder(
      BuildContext context, WidgetRef ref, String currentDir) async {
    try {
      final result = await FilePicker.platform.getDirectoryPath(
        dialogTitle: 'Select Download Folder',
        initialDirectory: currentDir.isNotEmpty ? currentDir : null,
      );

      if (result != null) {
        ref.read(settingsProvider.notifier).setDownloadFolder(result);
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to select folder: $e'),
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
            'Download Location',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        ListTile(
          leading: const Icon(Icons.folder_outlined),
          title: const Text('Download Folder'),
          subtitle: Text(
            settings.outputDir.isNotEmpty ? settings.outputDir : 'Not set',
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
          title: const Text('Auto-open Folder'),
          subtitle: const Text('Open folder after download completes'),
          value: settings.autoOpen,
          onChanged: (value) {
            ref.read(settingsProvider.notifier).updateConfig(autoOpen: value);
          },
        ),
      ],
    );
  }
}
