import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../services/backend_service.dart';
export '../services/notification_service.dart';

/// Backend service provider - manages backend process
final backendServiceProvider = Provider<BackendService>((ref) {
  return BackendService();
});

/// Backend port provider
final backendPortProvider = Provider<int>((ref) {
  final service = ref.watch(backendServiceProvider);
  return service.port;
});

/// API client provider (depends on port)
final apiClientProvider = Provider<ApiClient>((ref) {
  final port = ref.watch(backendPortProvider);
  return ApiClient(port);
});

/// Theme mode provider
class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  ThemeModeNotifier() : super(ThemeMode.system);

  void setThemeMode(ThemeMode mode) {
    state = mode;
  }

  void toggleTheme() {
    state = state == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
  }
}

final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>((ref) {
  return ThemeModeNotifier();
});
