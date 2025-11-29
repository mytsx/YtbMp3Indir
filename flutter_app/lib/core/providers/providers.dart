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
class ThemeModeNotifier extends Notifier<ThemeMode> {
  late SettingsService _settingsService;

  @override
  ThemeMode build() {
    _settingsService = ref.watch(settingsServiceProvider);
    return _settingsService.getThemeMode();
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

final themeModeProvider =
    NotifierProvider<ThemeModeNotifier, ThemeMode>(ThemeModeNotifier.new);

/// Theme style provider with persistence
class ThemeStyleNotifier extends Notifier<String> {
  late SettingsService _settingsService;

  @override
  String build() {
    _settingsService = ref.watch(settingsServiceProvider);
    return _settingsService.getThemeStyle();
  }

  void setThemeStyle(String style) {
    state = style;
    _settingsService.setThemeStyle(style);
  }
}

final themeStyleProvider =
    NotifierProvider<ThemeStyleNotifier, String>(ThemeStyleNotifier.new);

/// Notification settings notifier with persistence
class NotificationSettingsNotifier extends Notifier<NotificationSettings> {
  late SettingsService _settingsService;

  @override
  NotificationSettings build() {
    _settingsService = ref.watch(settingsServiceProvider);
    return NotificationSettings(
      soundEnabled: _settingsService.getNotificationSoundEnabled(),
    );
  }

  void setSoundEnabled(bool enabled) {
    state = state.copyWith(soundEnabled: enabled);
    _settingsService.setNotificationSoundEnabled(enabled);
  }

  void toggleSound() {
    setSoundEnabled(!state.soundEnabled);
  }
}

/// Notification settings provider with persistence
final notificationSettingsProvider =
    NotifierProvider<NotificationSettingsNotifier, NotificationSettings>(
        NotificationSettingsNotifier.new);
