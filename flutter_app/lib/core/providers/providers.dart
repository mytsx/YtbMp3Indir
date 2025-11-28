import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../services/backend_service.dart';
import '../services/settings_service.dart';
import '../services/notification_service.dart';
export '../services/notification_service.dart';

/// Settings service provider (singleton)
final settingsServiceProvider = Provider<SettingsService>((ref) {
  // This provider must be overridden in the ProviderScope/ProviderContainer.
  // It is initialized in main.dart before the app starts.
  throw UnimplementedError(
      'settingsServiceProvider must be overridden. Initialize in main.dart');
});

/// Backend service provider - manages backend process
final backendServiceProvider = Provider<BackendService>((ref) {
  return BackendService();
});

/// Backend port provider
final backendPortProvider = Provider<int>((ref) {
  final service = ref.watch(backendServiceProvider);
  return service.port;
});

/// API client provider (depends on port)
final apiClientProvider = Provider<ApiClient>((ref) {
  final port = ref.watch(backendPortProvider);
  return ApiClient(port);
});

/// Theme mode provider with persistence
class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  final SettingsService _settingsService;

  ThemeModeNotifier(this._settingsService) : super(ThemeMode.system) {
    // Load saved theme mode
    state = _settingsService.getThemeMode();
  }

  void setThemeMode(ThemeMode mode) {
    state = mode;
    _settingsService.setThemeMode(mode);
  }

  void toggleTheme() {
    final newMode = state == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
    setThemeMode(newMode);
  }
}

final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>((ref) {
  final settingsService = ref.watch(settingsServiceProvider);
  return ThemeModeNotifier(settingsService);
});

/// Notification settings provider with persistence
final notificationSettingsProvider =
    StateNotifierProvider<NotificationSettingsNotifier, NotificationSettings>(
        (ref) {
  final settingsService = ref.watch(settingsServiceProvider);
  return NotificationSettingsNotifier(settingsService);
});
