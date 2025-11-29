import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/history_item.dart';
import '../../../core/providers/providers.dart';

/// History list state notifier
class HistoryNotifier extends StateNotifier<AsyncValue<List<HistoryItem>>> {
  HistoryNotifier(this.ref) : super(const AsyncValue.loading()) {
    _loadHistory();
  }

  final Ref ref;
  int _currentOffset = 0;
  final int _pageSize = 50;
  bool _hasMore = true;

  /// Load initial history
  Future<void> _loadHistory() async {
    final apiClient = ref.read(apiClientProvider);

    try {
      final response = await apiClient.getHistory(limit: _pageSize, offset: 0);
      final items = (response['data'] as List)
          .map((json) => HistoryItem.fromJson(json))
          .toList();

      _hasMore = items.length == _pageSize;
      _currentOffset = items.length;
      state = AsyncValue.data(items);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Refresh history
  Future<void> refresh() async {
    _currentOffset = 0;
    _hasMore = true;
    await _loadHistory();
  }

  /// Load more items (pagination)
  Future<void> loadMore() async {
    if (!_hasMore || state.isLoading) return;

    final apiClient = ref.read(apiClientProvider);
    final currentItems = state.value ?? [];

    try {
      final response = await apiClient.getHistory(
        limit: _pageSize,
        offset: _currentOffset,
      );
      final newItems = (response['data'] as List)
          .map((json) => HistoryItem.fromJson(json))
          .toList();

      _hasMore = newItems.length == _pageSize;
      _currentOffset += newItems.length;

      state = AsyncValue.data([...currentItems, ...newItems]);
    } catch (_) {
      // Keep current state on error, silently ignore pagination errors
    }
  }

  /// Delete history item
  Future<bool> deleteItem(int id) async {
    final apiClient = ref.read(apiClientProvider);

    try {
      await apiClient.deleteHistoryItem(id);

      // Remove from state
      final currentItems = state.value ?? [];
      state = AsyncValue.data(
        currentItems.where((item) => item.id != id).toList(),
      );

      return true;
    } catch (_) {
      return false;
    }
  }
}

/// History provider
final historyProvider =
    StateNotifierProvider<HistoryNotifier, AsyncValue<List<HistoryItem>>>(
  (ref) => HistoryNotifier(ref),
);

/// Statistics provider
final statsProvider = FutureProvider<DownloadStats>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.getStatistics();
  return DownloadStats.fromJson(response['data']);
});

/// Search history provider
final searchHistoryProvider =
    FutureProvider.family<List<HistoryItem>, String>((ref, query) async {
  if (query.isEmpty) {
    return ref.watch(historyProvider).value ?? [];
  }

  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.searchHistory(query);
  return (response['data'] as List)
      .map((json) => HistoryItem.fromJson(json))
      .toList();
});

/// Redownload provider
final redownloadProvider = FutureProvider.family<void, int>((ref, historyId) async {
  final apiClient = ref.watch(apiClientProvider);
  await apiClient.redownload(historyId);
});
