import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../../../core/providers/providers.dart';

/// Settings screen for application configuration
class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  String _quality = '192';
  String _outputDir = '';
  bool _autoOpen = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    try {
      final apiClient = ref.read(apiClientProvider);
      if (apiClient == null) return;

      final response = await apiClient.getConfig();

      setState(() {
        _quality = response['quality'] ?? '192';
        _outputDir = response['output_dir'] ?? '';
        _autoOpen = response['auto_open'] ?? true;
      });
    } catch (e) {
      // Ignore errors during load
    }
  }

  Future<void> _selectDownloadFolder() async {
    try {
      final result = await FilePicker.platform.getDirectoryPath(
        dialogTitle: 'Select Download Folder',
        initialDirectory: _outputDir.isNotEmpty ? _outputDir : null,
      );

      if (result != null) {
        setState(() => _outputDir = result);
        await _saveConfig();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to select folder: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _saveConfig() async {
    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      if (apiClient == null) return;

      await apiClient.updateConfig({
        'quality': _quality,
        'output_dir': _outputDir,
        'auto_open': _autoOpen,
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Settings saved'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          if (_isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
        ],
      ),
      body: ListView(
        children: [
          // Audio Quality Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Audio Quality',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          RadioListTile<String>(
            title: const Text('128 kbps (Smaller file size)'),
            value: '128',
            groupValue: _quality,
            onChanged: (value) {
              setState(() => _quality = value!);
              _saveConfig();
            },
          ),
          RadioListTile<String>(
            title: const Text('192 kbps (Recommended)'),
            value: '192',
            groupValue: _quality,
            onChanged: (value) {
              setState(() => _quality = value!);
              _saveConfig();
            },
          ),
          RadioListTile<String>(
            title: const Text('256 kbps (High quality)'),
            value: '256',
            groupValue: _quality,
            onChanged: (value) {
              setState(() => _quality = value!);
              _saveConfig();
            },
          ),
          RadioListTile<String>(
            title: const Text('320 kbps (Best quality)'),
            value: '320',
            groupValue: _quality,
            onChanged: (value) {
              setState(() => _quality = value!);
              _saveConfig();
            },
          ),

          const Divider(),

          // Download Location Section
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
              _outputDir.isNotEmpty ? _outputDir : 'Not set',
              style: TextStyle(
                color: _outputDir.isNotEmpty ? null : Colors.grey,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: _selectDownloadFolder,
          ),

          const Divider(),

          // Appearance Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Appearance',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                const Icon(Icons.palette_outlined),
                const SizedBox(width: 16),
                const Expanded(
                  child: Text('Theme'),
                ),
                SegmentedButton<ThemeMode>(
                  segments: const [
                    ButtonSegment<ThemeMode>(
                      value: ThemeMode.system,
                      icon: Icon(Icons.settings_suggest),
                      label: Text('System'),
                    ),
                    ButtonSegment<ThemeMode>(
                      value: ThemeMode.light,
                      icon: Icon(Icons.light_mode),
                      label: Text('Light'),
                    ),
                    ButtonSegment<ThemeMode>(
                      value: ThemeMode.dark,
                      icon: Icon(Icons.dark_mode),
                      label: Text('Dark'),
                    ),
                  ],
                  selected: {ref.watch(themeModeProvider)},
                  onSelectionChanged: (selected) {
                    ref.read(themeModeProvider.notifier).setThemeMode(selected.first);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),

          const Divider(),

          // Notifications Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Notifications',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          SwitchListTile(
            title: const Text('Notification sound'),
            subtitle: const Text('Play a sound when download completes'),
            secondary: const Icon(Icons.notifications_outlined),
            value: ref.watch(notificationSettingsProvider).soundEnabled,
            onChanged: (value) {
              ref.read(notificationSettingsProvider.notifier).setSoundEnabled(value);
              // Test the sound when enabling
              if (value) {
                ref.read(notificationServiceProvider).playCompletionSound();
              }
            },
          ),

          const Divider(),

          // Other Settings
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Other Settings',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          SwitchListTile(
            title: const Text('Auto-open downloads'),
            subtitle: const Text('Automatically open files after download'),
            value: _autoOpen,
            onChanged: (value) {
              setState(() => _autoOpen = value);
              _saveConfig();
            },
          ),

          const Divider(),

          // About Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'About',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'MP3 Yap',
                  style: theme.textTheme.titleLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  'Version 1.0.0',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'YouTube MP3 Downloader with Flutter',
                  style: theme.textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
