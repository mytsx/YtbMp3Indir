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
                key: const ValueKey('theme_mode_selector'),
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
              const Expanded(
                child: Text('Style'),
              ),
              DropdownButton<String>(
                value: ref.watch(themeStyleProvider),
                items: const [
                  DropdownMenuItem(
                    value: 'cyberpunk',
                    child: Text('Cyberpunk'),
                  ),
                  DropdownMenuItem(
                    value: 'neopop',
                    child: Text('NeoPop'),
                  ),
                  DropdownMenuItem(
                    value: 'classic',
                    child: Text('Classic'),
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
