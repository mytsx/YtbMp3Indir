import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Global audio player instance
final audioPlayerProvider = Provider<AudioPlayer>((ref) {
  final player = AudioPlayer();
  
  // Cleanup on dispose
  ref.onDispose(() {
    player.dispose();
  });
  
  return player;
});

/// Currently playing file provider
final currentlyPlayingProvider = StateProvider<String?>((ref) => null);

/// Player state provider
final playerStateProvider = StreamProvider<PlayerState>((ref) {
  final player = ref.watch(audioPlayerProvider);
  return player.onPlayerStateChanged;
});
