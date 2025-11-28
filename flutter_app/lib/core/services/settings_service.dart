import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for persisting app settings locally
class SettingsService {
  static const String _themeModeKey = 'theme_mode';
  static const String _notificationSoundKey = 'notification_sound';

  SharedPreferences? _prefsInstance;

  /// Get SharedPreferences instance (throws if not initialized)
  SharedPreferences get _prefs {
    if (_prefsInstance == null) {
      throw StateError(
          'SettingsService has not been initialized. Call init() before use.');
    }
    return _prefsInstance!;
  }

  /// Initialize the service (must be called before using)
  Future<void> init() async {
    _prefsInstance = await SharedPreferences.getInstance();
  }

  /// Get saved theme mode
  ThemeMode getThemeMode() {
    final value = _prefs.getString(_themeModeKey);
    return ThemeMode.values.firstWhere(
      (e) => e.name == value,
      orElse: () => ThemeMode.system,
    );
  }

  /// Save theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    await _prefs.setString(_themeModeKey, mode.name);
  }

  /// Get notification sound enabled
  bool getNotificationSoundEnabled() {
    return _prefs.getBool(_notificationSoundKey) ?? true;
  }

  /// Save notification sound enabled
  Future<void> setNotificationSoundEnabled(bool enabled) async {
    await _prefs.setBool(_notificationSoundKey, enabled);
  }
}
