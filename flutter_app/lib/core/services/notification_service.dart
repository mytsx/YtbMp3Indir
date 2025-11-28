import 'dart:developer' as developer;
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'settings_service.dart';

/// Notification settings state
class NotificationSettings {
  final bool soundEnabled;

  const NotificationSettings({
    this.soundEnabled = true,
  });

  NotificationSettings copyWith({
    bool? soundEnabled,
  }) {
    return NotificationSettings(
      soundEnabled: soundEnabled ?? this.soundEnabled,
    );
  }
}

/// Notification settings notifier with persistence
class NotificationSettingsNotifier extends StateNotifier<NotificationSettings> {
  final SettingsService _settingsService;

  NotificationSettingsNotifier(this._settingsService)
      : super(const NotificationSettings()) {
    // Load saved setting
    state = NotificationSettings(
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

/// Notification service for playing sounds
class NotificationService {
  final AudioPlayer _player = AudioPlayer();
  bool _isInitialized = false;

  Future<void> _ensureInitialized() async {
    if (!_isInitialized) {
      await _player.setReleaseMode(ReleaseMode.stop);
      _isInitialized = true;
    }
  }

  /// Play completion notification sound
  Future<void> playCompletionSound() async {
    try {
      await _ensureInitialized();
      await _player.play(
        AssetSource('sounds/completion.wav'),
        volume: 0.5,
      );
    } catch (e, stackTrace) {
      developer.log(
        'Failed to play completion sound',
        error: e,
        stackTrace: stackTrace,
        name: 'NotificationService',
      );
    }
  }

  /// Play error notification sound
  Future<void> playErrorSound() async {
    try {
      await _ensureInitialized();
      await _player.play(
        AssetSource('sounds/error.wav'),
        volume: 0.4,
      );
    } catch (e, stackTrace) {
      developer.log(
        'Failed to play error sound',
        error: e,
        stackTrace: stackTrace,
        name: 'NotificationService',
      );
    }
  }

  void dispose() {
    _player.dispose();
  }
}

/// Notification service provider
final notificationServiceProvider = Provider<NotificationService>((ref) {
  final service = NotificationService();
  ref.onDispose(() => service.dispose());
  return service;
});
