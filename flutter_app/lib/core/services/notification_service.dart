import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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

/// Notification settings notifier
class NotificationSettingsNotifier extends StateNotifier<NotificationSettings> {
  NotificationSettingsNotifier() : super(const NotificationSettings());

  void setSoundEnabled(bool enabled) {
    state = state.copyWith(soundEnabled: enabled);
  }

  void toggleSound() {
    state = state.copyWith(soundEnabled: !state.soundEnabled);
  }
}

/// Notification settings provider
final notificationSettingsProvider =
    StateNotifierProvider<NotificationSettingsNotifier, NotificationSettings>(
        (ref) {
  return NotificationSettingsNotifier();
});

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

      // Use a simple system-like notification sound from a reliable source
      // This is a short, pleasant notification sound
      await _player.play(
        UrlSource(
          'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3',
        ),
        volume: 0.5,
      );
    } catch (_) {
      // Silently fail if sound can't be played
    }
  }

  /// Play error notification sound
  Future<void> playErrorSound() async {
    try {
      await _ensureInitialized();

      await _player.play(
        UrlSource(
          'https://assets.mixkit.co/active_storage/sfx/2955/2955-preview.mp3',
        ),
        volume: 0.4,
      );
    } catch (_) {
      // Silently fail if sound can't be played
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
