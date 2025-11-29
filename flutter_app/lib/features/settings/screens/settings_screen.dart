import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart';
import '../../../core/theme/cyberpunk_colors.dart';
import '../../../core/providers/providers.dart';
import '../providers/settings_provider.dart';
import '../widgets/appearance_section.dart';
import '../widgets/audio_quality_section.dart';
import '../widgets/download_location_section.dart';
import '../widgets/history_retention_section.dart';
import '../widgets/language_section.dart';
import '../widgets/notifications_section.dart';

/// Settings screen for application configuration
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final theme = Theme.of(context);
    final themeStyle = ref.watch(themeStyleProvider);
    final isCyberpunk = themeStyle == 'cyberpunk';
    final isDarkMode = theme.brightness == Brightness.dark;

    // Show error snackbar if error exists
    ref.listen(settingsProvider, (previous, next) {
      if (next.error != null && next.error != previous?.error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('settings.error_prefix'.tr(args: [next.error!])),
            backgroundColor:
                isCyberpunk ? CyberpunkColors.neonPinkGlow : Colors.red,
          ),
        );
      }
      if (next.successMessage != null &&
          next.successMessage != previous?.successMessage) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next.successMessage!),
            backgroundColor:
                isCyberpunk ? CyberpunkColors.matrixGreen : Colors.green,
          ),
        );
      }
    });

    return Scaffold(
      backgroundColor: (isCyberpunk && isDarkMode) ? Colors.transparent : null,
      appBar: AppBar(
        backgroundColor:
            (isCyberpunk && isDarkMode) ? Colors.transparent : null,
        title: Text('settings.title'.tr()),
        actions: [
          if (settings.isLoading)
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
          const LanguageSection(),
          const Divider(),
          const AudioQualitySection(),
          const Divider(),
          const DownloadLocationSection(),
          const Divider(),
          const AppearanceSection(),
          const Divider(),
          const NotificationsSection(),
          const Divider(),
          const HistoryRetentionSection(),
          const Divider(),

          // About Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'settings.about'.tr(),
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
                  '${'settings.version'.tr()} 1.0.0',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'settings.app_description'.tr(),
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
