import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Service to handle dynamic language loading from assets
class LanguageService {
  static final LanguageService _instance = LanguageService._internal();
  factory LanguageService() => _instance;
  LanguageService._internal();

  final List<Locale> _supportedLocales = [];
  final Map<String, String> _languageNames = {};

  List<Locale> get supportedLocales => List.unmodifiable(_supportedLocales);

  /// Initialize the service by scanning assets
  Future<void> init() async {
    try {
      // Load asset manifest
      final manifestContent = await rootBundle.loadString('AssetManifest.json');
      final Map<String, dynamic> manifestMap = json.decode(manifestContent);

      // Find all translation files
      final translationFiles = manifestMap.keys
          .where((key) =>
              key.startsWith('assets/translations/') && key.endsWith('.json'))
          .toList();

      _supportedLocales.clear();
      _languageNames.clear();

      for (final filePath in translationFiles) {
        // Parse locale from filename (e.g., "assets/translations/en-US.json" -> "en-US")
        final fileName = filePath.split('/').last;
        final localeTag = fileName.split('.').first;
        final parts = localeTag.split('-');

        if (parts.isNotEmpty) {
          final locale = Locale(parts[0], parts.length > 1 ? parts[1] : null);
          _supportedLocales.add(locale);

          // Read file content to get language name
          try {
            final content = await rootBundle.loadString(filePath);
            final jsonContent = json.decode(content);
            if (jsonContent is Map<String, dynamic> &&
                jsonContent.containsKey('meta') &&
                jsonContent['meta'] is Map &&
                jsonContent['meta'].containsKey('language_name')) {
              _languageNames[locale.toString()] =
                  jsonContent['meta']['language_name'];
            }
          } catch (e) {
            debugPrint('Error reading language name for $localeTag: $e');
          }
        }
      }

      // Sort locales: English first, then others alphabetically
      _supportedLocales.sort((a, b) {
        if (a.languageCode == 'en') return -1;
        if (b.languageCode == 'en') return 1;
        return a.toString().compareTo(b.toString());
      });

      debugPrint(
          'Loaded ${_supportedLocales.length} languages: $_supportedLocales');
    } catch (e) {
      debugPrint('Error initializing LanguageService: $e');
      // Fallback to default
      _supportedLocales.add(const Locale('en', 'US'));
      _supportedLocales.add(const Locale('tr', 'TR'));
    }
  }

  /// Get display name for a locale
  String getLanguageName(Locale locale) {
    return _languageNames[locale.toString()] ??
        locale.languageCode.toUpperCase();
  }
}
