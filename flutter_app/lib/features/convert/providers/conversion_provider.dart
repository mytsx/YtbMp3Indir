import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../core/providers/providers.dart';
import '../../../core/models/conversion.dart';

/// Current conversions list provider
class ConversionsNotifier extends StateNotifier<List<Conversion>> {
  ConversionsNotifier() : super([]);

  void addConversion(Conversion conversion) {
    state = [...state, conversion];
  }

  void updateConversion(String id, Conversion updated) {
    state = [
      for (final conversion in state)
        if (conversion.id == id) updated else conversion
    ];
  }

  void removeConversion(String id) {
    state = state.where((c) => c.id != id).toList();
  }

  void clear() {
    state = [];
  }
}

final conversionsProvider =
    StateNotifierProvider<ConversionsNotifier, List<Conversion>>((ref) {
  return ConversionsNotifier();
});

/// Start conversion provider
final startConversionProvider =
    FutureProvider.family<Conversion, String>((ref, filePath) async {
  final apiClient = ref.read(apiClientProvider);

  if (apiClient == null) {
    throw Exception('Backend not ready');
  }

  // Call API to start conversion
  final result = await apiClient.startConversion(filePath);

  // Parse response to Conversion model
  final conversion = Conversion.fromJson(result);

  // Add to conversions list
  ref.read(conversionsProvider.notifier).addConversion(conversion);

  return conversion;
});

/// WebSocket progress stream provider for conversion
final conversionProgressProvider =
    StreamProvider.family<ConversionProgressUpdate, String>((ref, conversionId) {
  final port = ref.watch(backendPortProvider);

  final wsUrl = 'ws://127.0.0.1:$port/ws/download/$conversionId';
  final channel = WebSocketChannel.connect(Uri.parse(wsUrl));

  ref.onDispose(() {
    channel.sink.close();
  });

  return channel.stream.map((data) {
    final json = jsonDecode(data as String) as Map<String, dynamic>;
    final update = ConversionProgressUpdate.fromJson(json);

    // Update conversion in list
    final conversions = ref.read(conversionsProvider);
    final conversionIndex = conversions.indexWhere((c) => c.id == conversionId);

    // Handle case where conversion is not found (may have been removed)
    if (conversionIndex == -1) {
      return update;
    }

    final conversion = conversions[conversionIndex];
    Conversion updated = conversion;

    switch (update.type) {
      case 'progress':
        updated = conversion.copyWith(
          progress: update.progress,
        );
        break;

      case 'status':
        updated = conversion.copyWith(
          status: update.status ?? conversion.status,
          progress: update.progress ?? conversion.progress,
        );
        break;

      case 'completed':
        updated = conversion.copyWith(
          status: 'completed',
          progress: 100,
          outputPath: update.outputPath,
        );
        // Play notification sound if enabled
        final notificationSettings = ref.read(notificationSettingsProvider);
        if (notificationSettings.soundEnabled) {
          ref.read(notificationServiceProvider).playCompletionSound();
        }
        break;

      case 'error':
        updated = conversion.copyWith(
          status: 'failed',
          error: update.error,
        );
        break;
    }

    ref.read(conversionsProvider.notifier).updateConversion(conversionId, updated);

    return update;
  });
});
