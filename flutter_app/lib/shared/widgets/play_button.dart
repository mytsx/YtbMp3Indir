import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:audioplayers/audioplayers.dart';
import '../../features/player/audio_player_provider.dart';

class PlayButton extends ConsumerWidget {
  final String filePath;
  final Color? color;
  final double size;

  const PlayButton({
    super.key,
    required this.filePath,
    this.color,
    this.size = 28,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final player = ref.watch(audioPlayerProvider);
    final currentlyPlaying = ref.watch(currentlyPlayingProvider);
    final playerStateAsync = ref.watch(playerStateProvider);
    final theme = Theme.of(context);

    final isThisPlaying = currentlyPlaying == filePath;
    final isPlaying = playerStateAsync.value == PlayerState.playing && isThisPlaying;

    return IconButton(
      icon: Icon(
        isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled,
        size: size,
      ),
      color: color ?? theme.colorScheme.primary,
      onPressed: () async {
        if (isThisPlaying && isPlaying) {
          // Pause
          await player.pause();
        } else if (isThisPlaying) {
          // Resume
          await player.resume();
        } else {
          // Play new file
          String absolutePath = filePath;

          // Convert relative paths to absolute if needed
          if (!absolutePath.startsWith('/')) {
            final file = File(absolutePath);
            absolutePath = file.absolute.path;
          }

          // Verify file exists before playing
          if (!await File(absolutePath).exists()) {
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('File not found: $absolutePath'),
                  backgroundColor: Colors.red,
                ),
              );
            }
            return;
          }

          await player.stop();
          await player.play(DeviceFileSource(absolutePath));
          ref.read(currentlyPlayingProvider.notifier).state = absolutePath;
        }
      },
    );
  }
}
