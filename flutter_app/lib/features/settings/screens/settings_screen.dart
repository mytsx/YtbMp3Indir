import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/providers.dart';

/// Settings screen for application configuration
class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  String _quality = '192';
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
        _autoOpen = response['auto_open'] ?? true;
      });
    } catch (e) {
      // Ignore errors during load
    }
  }

  Future<void> _saveConfig() async {
    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      if (apiClient == null) return;

      await apiClient.updateConfig({
        'quality': _quality,
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
