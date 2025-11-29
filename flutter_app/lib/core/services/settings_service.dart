import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for persisting app settings locally
class SettingsService {
  static const String _themeModeKey = 'theme_mode';
  static const String _themeStyleKey = 'theme_style';
  static const String _notificationSoundKey = 'notification_sound';
  static const String _isFirstRunKey = 'is_first_run';

  late final SharedPreferences _prefs;

  /// Initialize the service (must be called before using)
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Check if this is the first run
  bool getIsFirstRun() {
    return _prefs.getBool(_isFirstRunKey) ?? true;
  }

  /// Mark first run as completed
  Future<void> setFirstRunCompleted() async {
    await _prefs.setBool(_isFirstRunKey, false);
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

  /// Get saved theme style (cyberpunk, classic)
  String getThemeStyle() {
    return _prefs.getString(_themeStyleKey) ?? 'cyberpunk';
  }

  /// Save theme style
  Future<void> setThemeStyle(String style) async {
    await _prefs.setString(_themeStyleKey, style);
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
