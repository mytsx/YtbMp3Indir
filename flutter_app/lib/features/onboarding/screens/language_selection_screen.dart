import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/providers.dart';

class LanguageSelectionScreen extends ConsumerWidget {
  final VoidCallback onContinue;

  const LanguageSelectionScreen({
    super.key,
    required this.onContinue,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    
    return Scaffold(
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.language, size: 64),
              const SizedBox(height: 32),
              Text(
                'common.language_selection'.tr(),
                style: theme.textTheme.headlineMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              _buildLanguageOption(
                context,
                'Türkçe',
                const Locale('tr', 'TR'),
              ),
              const SizedBox(height: 16),
              _buildLanguageOption(
                context,
                'English',
                const Locale('en', 'US'),
              ),
              const SizedBox(height: 48),
              FilledButton(
                onPressed: () async {
                  final settingsService = ref.read(settingsServiceProvider);
                  await settingsService.setFirstRunCompleted();
                  onContinue();
                },
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text('common.continue'.tr()),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageOption(
    BuildContext context,
    String label,
    Locale locale,
  ) {
    final isSelected = context.locale == locale;
    final theme = Theme.of(context);

    return InkWell(
      onTap: () => context.setLocale(locale),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: isSelected ? theme.primaryColor : theme.dividerColor,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(12),
          color: isSelected ? theme.primaryColor.withValues(alpha: 0.1) : null,
        ),
        child: Row(
          children: [
            Text(
              label,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: isSelected ? FontWeight.bold : null,
              ),
            ),
            const Spacer(),
            if (isSelected)
              Icon(Icons.check_circle, color: theme.primaryColor),
          ],
        ),
      ),
    );
  }
}
