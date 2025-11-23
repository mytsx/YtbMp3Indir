import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../core/providers/providers.dart';
import '../../../core/models/download.dart';

/// Current downloads list provider (state notifier)
class DownloadsNotifier extends StateNotifier<List<Download>> {
  DownloadsNotifier() : super([]);

  void addDownload(Download download) {
    state = [...state, download];
  }

  void updateDownload(String id, Download updated) {
    state = [
      for (final download in state)
        if (download.id == id) updated else download
    ];
  }

  void removeDownload(String id) {
    state = state.where((d) => d.id != id).toList();
  }

  void clear() {
    state = [];
  }
}

final downloadsProvider =
    StateNotifierProvider<DownloadsNotifier, List<Download>>((ref) {
  return DownloadsNotifier();
});

/// Start download provider (callable)
final startDownloadProvider =
    FutureProvider.family<Download, String>((ref, url) async {
  final apiClient = ref.read(apiClientProvider);

  if (apiClient == null) {
    throw Exception('Backend not ready');
  }

  // Call API to start download
  final result = await apiClient.startDownload(url);

  // Parse response to Download model
  final download = Download.fromJson(result);

  // Add to downloads list
  ref.read(downloadsProvider.notifier).addDownload(download);

  return download;
});

/// WebSocket progress stream provider (family for each download)
final downloadProgressProvider =
    StreamProvider.family<ProgressUpdate, String>((ref, downloadId) {
  // Get port from backend
  final port = ref.watch(backendPortProvider);

  final wsUrl = 'ws://127.0.0.1:$port/ws/download/$downloadId';
  final channel = WebSocketChannel.connect(Uri.parse(wsUrl));

  // Clean up on dispose
  ref.onDispose(() {
    channel.sink.close();
  });

  // Map WebSocket messages to ProgressUpdate
      return channel.stream.map((data) {
        final json = jsonDecode(data as String) as Map<String, dynamic>;
        final update = ProgressUpdate.fromJson(json);

        // Update download in list
        final downloads = ref.read(downloadsProvider);
        final download = downloads.firstWhere((d) => d.id == downloadId);

        // Create updated download based on progress update
        Download updated = download;

        switch (update.type) {
          case 'progress':
            updated = download.copyWith(
              progress: update.progress,
              speed: update.speed,
              eta: update.eta,
            );
            break;

          case 'status':
            updated = download.copyWith(
              status: update.status ?? download.status,
            );
            break;

          case 'info':
            updated = download.copyWith(
              videoTitle: update.videoTitle ?? download.videoTitle,
            );
            break;

          case 'completed':
            updated = download.copyWith(
              status: 'completed',
              progress: 100,
              filePath: update.filePath,
            );
            break;

          case 'error':
            updated = download.copyWith(
              status: 'failed',
              error: update.error,
            );
            break;
        }

        // Update in provider
        ref.read(downloadsProvider.notifier).updateDownload(downloadId, updated);

        return update;
      });
});
