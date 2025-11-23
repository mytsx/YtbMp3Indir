import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/backend_service.dart';
import '../api/api_client.dart';

/// Backend service provider
final backendServiceProvider = Provider<BackendService>((ref) {
  final service = BackendService();

  // Cleanup on dispose
  ref.onDispose(() {
    service.stop();
  });

  return service;
});

/// Backend port provider (async)
final backendPortProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(backendServiceProvider);

  // Start backend if not running
  if (!service.isRunning) {
    await service.start();
  }

  return service.port!;
});

/// API client provider (depends on port)
final apiClientProvider = Provider<ApiClient?>((ref) {
  final portAsync = ref.watch(backendPortProvider);

  return portAsync.when(
    data: (port) => ApiClient(port),
    loading: () => null,
    error: (err, stack) {
      // Log error
      print('Backend error: $err');
      return null;
    },
  );
});
