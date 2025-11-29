import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/empty_state_widget.dart';
import '../../../shared/widgets/error_state_widget.dart';
import '../providers/history_provider.dart';
import '../widgets/history_card.dart';

/// History screen displaying download history with search and statistics
class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();
  String _searchQuery = '';
  bool _isSearching = false;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_isSearching) return; // Don't paginate when searching

    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(historyProvider.notifier).loadMore();
    }
  }

  void _onSearchChanged(String query) {
    setState(() {
      _searchQuery = query;
      _isSearching = query.isNotEmpty;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Use search provider when searching, otherwise use history provider
    final historyAsync = _isSearching
        ? ref.watch(searchHistoryProvider(_searchQuery))
        : ref.watch(historyProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Download History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              if (_isSearching) {
                ref.invalidate(searchHistoryProvider(_searchQuery));
              } else {
                ref.read(historyProvider.notifier).refresh();
              }
            },
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: 'Search downloads...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _onSearchChanged('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),

          // History list
          Expanded(
            child: historyAsync.when(
              data: (items) {
                if (items.isEmpty) {
                  return EmptyStateWidget(
                    icon: _isSearching ? Icons.search_off : Icons.history,
                    title: _isSearching ? 'No results found' : 'No download history',
                    subtitle: _isSearching
                        ? 'Try a different search query'
                        : 'Your downloads will appear here',
                  );
                }

                return RefreshIndicator(
                  onRefresh: () async {
                    if (_isSearching) {
                      ref.invalidate(searchHistoryProvider(_searchQuery));
                    } else {
                      await ref.read(historyProvider.notifier).refresh();
                    }
                  },
                  child: ListView.builder(
                    controller: _scrollController,
                    itemCount: items.length + 1, // +1 for loading indicator
                    itemBuilder: (context, index) {
                      if (index == items.length) {
                        // Show loading indicator at bottom when paginating
                        if (!_isSearching) {
                          return const Padding(
                            padding: EdgeInsets.all(16),
                            child: SizedBox.shrink(),
                          );
                        }
                        return const SizedBox.shrink();
                      }

                      return HistoryCard(item: items[index]);
                    },
                  ),
                );
              },
              loading: () => const Center(
                child: CircularProgressIndicator(),
              ),
              error: (error, stack) => ErrorStateWidget(
                message: error.toString(),
                onRetry: () {
                  if (_isSearching) {
                    ref.invalidate(searchHistoryProvider(_searchQuery));
                  } else {
                    ref.read(historyProvider.notifier).refresh();
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
