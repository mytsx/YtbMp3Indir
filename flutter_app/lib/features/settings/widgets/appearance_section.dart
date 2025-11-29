import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/providers.dart';

class AppearanceSection extends ConsumerWidget {
  const AppearanceSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final currentThemeMode = ref.watch(themeModeProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'settings.appearance.title'.tr(),
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
              Expanded(
                child: Text('settings.appearance.theme.label'.tr()),
              ),
              SegmentedButton<ThemeMode>(
                key: const ValueKey('theme_mode_selector'),
                segments: [
                  ButtonSegment<ThemeMode>(
                    value: ThemeMode.system,
                    icon: const Icon(Icons.settings_suggest),
                    label: Text('settings.appearance.theme.system'.tr()),
                  ),
                  ButtonSegment<ThemeMode>(
                    value: ThemeMode.light,
                    icon: const Icon(Icons.light_mode),
                    label: Text('settings.appearance.theme.light'.tr()),
                  ),
                  ButtonSegment<ThemeMode>(
                    value: ThemeMode.dark,
                    icon: const Icon(Icons.dark_mode),
                    label: Text('settings.appearance.theme.dark'.tr()),
                  ),
                ],
                selected: {currentThemeMode},
                onSelectionChanged: (selected) {
                  ref
                      .read(themeModeProvider.notifier)
                      .setThemeMode(selected.first);
                },
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              const Icon(Icons.style_outlined),
              const SizedBox(width: 16),
              Expanded(
                child: Text('settings.appearance.style.label'.tr()),
              ),
              DropdownButton<String>(
                value: ref.watch(themeStyleProvider),
                items: [
                  DropdownMenuItem(
                    value: 'cyberpunk',
                    child: Text('settings.appearance.style.cyberpunk'.tr()),
                  ),
                  DropdownMenuItem(
                    value: 'neopop',
                    child: Text('settings.appearance.style.neopop'.tr()),
                  ),
                  DropdownMenuItem(
                    value: 'classic',
                    child: Text('settings.appearance.style.classic'.tr()),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) {
                    ref.read(themeStyleProvider.notifier).setThemeStyle(value);
                  }
                },
              ),
            ],
          ),
        ),
      ],
    );
  }
}
