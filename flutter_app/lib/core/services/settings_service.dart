import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for persisting app settings locally
class SettingsService {
  static const String _themeModeKey = 'theme_mode';
  static const String _notificationSoundKey = 'notification_sound';

  SharedPreferences? _prefs;

  /// Initialize the service (must be called before using)
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Get saved theme mode
  ThemeMode getThemeMode() {
    final value = _prefs?.getString(_themeModeKey);
    switch (value) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.system;
    }
  }

  /// Save theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    String value;
    switch (mode) {
      case ThemeMode.light:
        value = 'light';
        break;
      case ThemeMode.dark:
        value = 'dark';
        break;
      case ThemeMode.system:
        value = 'system';
        break;
    }
    await _prefs?.setString(_themeModeKey, value);
  }

  /// Get notification sound enabled
  bool getNotificationSoundEnabled() {
    return _prefs?.getBool(_notificationSoundKey) ?? true;
  }

  /// Save notification sound enabled
  Future<void> setNotificationSoundEnabled(bool enabled) async {
    await _prefs?.setBool(_notificationSoundKey, enabled);
  }
}
