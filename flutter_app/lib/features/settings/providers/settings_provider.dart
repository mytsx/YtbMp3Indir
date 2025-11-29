import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/providers.dart';

class SettingsState {
  final String quality;
  final String outputDir;
  final bool autoOpen;
  final int historyRetentionDays;
  final bool isLoading;
  final String? error;
  final String? successMessage;

  const SettingsState({
    this.quality = '192',
    this.outputDir = '',
    this.autoOpen = true,
    this.historyRetentionDays = 0,
    this.isLoading = false,
    this.error,
    this.successMessage,
  });

  SettingsState copyWith({
    String? quality,
    String? outputDir,
    bool? autoOpen,
    int? historyRetentionDays,
    bool? isLoading,
    String? error,
    String? successMessage,
  }) {
    return SettingsState(
      quality: quality ?? this.quality,
      outputDir: outputDir ?? this.outputDir,
      autoOpen: autoOpen ?? this.autoOpen,
      historyRetentionDays: historyRetentionDays ?? this.historyRetentionDays,
      isLoading: isLoading ?? this.isLoading,
      error:
          error, // Reset error on new state unless explicitly set (or handle differently)
      successMessage: successMessage, // Reset success message
    );
  }
}

class SettingsNotifier extends StateNotifier<SettingsState> {
  final Ref ref;

  SettingsNotifier(this.ref) : super(const SettingsState()) {
    loadConfig();
  }

  Future<void> loadConfig() async {
    state = state.copyWith(isLoading: true);
    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.getConfig();
      state = SettingsState(
        quality: response['quality'] ?? '192',
        outputDir: response['output_dir'] ?? '',
        autoOpen: response['auto_open'] ?? true,
        historyRetentionDays: response['history_retention_days'] ?? 0,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateConfig({
    String? quality,
    String? outputDir,
    bool? autoOpen,
    int? historyRetentionDays,
  }) async {
    state = state.copyWith(isLoading: true);
    try {
      final apiClient = ref.read(apiClientProvider);
      final newQuality = quality ?? state.quality;
      final newOutputDir = outputDir ?? state.outputDir;
      final newAutoOpen = autoOpen ?? state.autoOpen;
      final newHistoryRetentionDays =
          historyRetentionDays ?? state.historyRetentionDays;

      await apiClient.updateConfig({
        'quality': newQuality,
        'output_dir': newOutputDir,
        'auto_open': newAutoOpen,
        'history_retention_days': newHistoryRetentionDays,
      });

      state = state.copyWith(
        quality: newQuality,
        outputDir: newOutputDir,
        autoOpen: newAutoOpen,
        historyRetentionDays: newHistoryRetentionDays,
        isLoading: false,
        successMessage: 'Settings saved',
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> setDownloadFolder(String path) async {
    await updateConfig(outputDir: path);
  }
}

final settingsProvider =
    StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  return SettingsNotifier(ref);
});
