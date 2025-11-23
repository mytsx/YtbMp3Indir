import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';

/// Backend port provider
/// NOTE: Backend should be started manually with: cd backend && python main.py
/// This provider uses a fixed port for development
final backendPortProvider = Provider<int>((ref) {
  // Default port - backend will print actual port on startup
  // For development: start backend manually and update this if needed
  return 62221; // Update this based on backend output
});

/// API client provider (depends on port)
final apiClientProvider = Provider<ApiClient>((ref) {
  final port = ref.watch(backendPortProvider);
  return ApiClient(port);
});
