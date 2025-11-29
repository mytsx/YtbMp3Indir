import 'package:dio/dio.dart';

/// HTTP API Client for communicating with FastAPI backend
/// Uses Dio with dynamic baseUrl from discovered port
class ApiClient {
  final Dio _dio;
  final int port;

  ApiClient(this.port)
      : _dio = Dio(BaseOptions(
          baseUrl: 'http://127.0.0.1:$port',
          connectTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            'Content-Type': 'application/json',
          },
        )) {
    // Add logging interceptor (helpful for debugging)
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      requestHeader: false,
      responseHeader: false,
    ));
  }

  /// Generic response handler that processes ApiResponse envelope
  Future<T> _handleResponse<T>(
    Future<Response> request,
    T Function(dynamic) fromJson,
  ) async {
    try {
      final response = await request;
      final data = response.data;

      // Check success field
      if (data['success'] == true) {
        return fromJson(data['data']);
      } else {
        // API returned error
        final error = data['error'];
        throw ApiException(
          code: error['code'] ?? 'UNKNOWN',
          message: error['message'] ?? 'Unknown error',
        );
      }
    } on DioException catch (e) {
      // Network or parsing error
      throw ApiException(
        code: 'NETWORK_ERROR',
        message: e.message ?? 'Network error occurred',
      );
    }
  }

  // ==========================================================================
  // Health Check
  // ==========================================================================

  Future<Map<String, dynamic>> healthCheck() async {
    final response = await _dio.get('/api/health');
    return response.data as Map<String, dynamic>;
  }

  // ==========================================================================
  // Downloads
  // ==========================================================================

  Future<Map<String, dynamic>> startDownload(
    String url, {
    String quality = '192',
  }) {
    return _handleResponse(
      _dio.post('/api/downloads', data: {
        'url': url,
        'quality': quality,
      }),
      (data) => data as Map<String, dynamic>,
    );
  }

  Future<List<Map<String, dynamic>>> getDownloads() {
    return _handleResponse(
      _dio.get('/api/downloads'),
      (data) => (data as List).cast<Map<String, dynamic>>(),
    );
  }

  Future<Map<String, dynamic>> getDownload(String id) {
    return _handleResponse(
      _dio.get('/api/downloads/$id'),
      (data) => data as Map<String, dynamic>,
    );
  }

  Future<void> cancelDownload(String id) {
    return _handleResponse(
      _dio.delete('/api/downloads/$id'),
      (_) {},
    );
  }

  // ==========================================================================
  // History
  // ==========================================================================

  Future<Map<String, dynamic>> getHistory({
    int limit = 100,
    int offset = 0,
  }) {
    return _handleResponse(
      _dio.get('/api/history', queryParameters: {
        'limit': limit,
        'offset': offset,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  Future<Map<String, dynamic>> getHistoryItem(int id) {
    return _handleResponse(
      _dio.get('/api/history/$id'),
      (data) => data as Map<String, dynamic>,
    );
  }

  Future<Map<String, dynamic>> searchHistory(String query) {
    return _handleResponse(
      _dio.get('/api/history/search', queryParameters: {
        'q': query,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  Future<Map<String, dynamic>> getStatistics() {
    return _handleResponse(
      _dio.get('/api/history/stats'),
      (data) => {
        'data': data,
      },
    );
  }

  Future<void> deleteHistoryItem(int id) {
    return _handleResponse(
      _dio.delete('/api/history/$id'),
      (_) {},
    );
  }

  Future<Map<String, dynamic>> redownload(int id) {
    return _handleResponse(
      _dio.post('/api/history/$id/redownload'),
      (data) => {
        'data': data,
      },
    );
  }

  // ==========================================================================
  // Queue
  // ==========================================================================

  Future<Map<String, dynamic>> getQueue({
    int limit = 100,
    int offset = 0,
  }) {
    return _handleResponse(
      _dio.get('/api/queue', queryParameters: {
        'limit': limit,
        'offset': offset,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  Future<Map<String, dynamic>> addToQueue(String url, {int priority = 0}) {
    return _handleResponse(
      _dio.post('/api/queue', data: {
        'url': url,
        'priority': priority,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  Future<Map<String, dynamic>> updateQueuePriority(int queueId, int priority) {
    return _handleResponse(
      _dio.patch('/api/queue/$queueId/priority', data: {
        'priority': priority,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  Future<Map<String, dynamic>> updateQueuePosition(int queueId, int position) {
    return _handleResponse(
      _dio.patch('/api/queue/$queueId/position', data: {
        'position': position,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  Future<void> deleteQueueItem(int queueId) {
    return _handleResponse(
      _dio.delete('/api/queue/$queueId'),
      (_) {},
    );
  }

  Future<Map<String, dynamic>> clearQueue({String status = 'all'}) {
    return _handleResponse(
      _dio.post('/api/queue/clear', data: {
        'status': status,
      }),
      (data) => {
        'data': data,
      },
    );
  }

  // ==========================================================================
  // Conversions
  // ==========================================================================

  Future<Map<String, dynamic>> startConversion(
    String filePath, {
    String quality = '320',
    String outputFormat = 'mp3',
  }) {
    return _handleResponse(
      _dio.post('/api/conversions', data: {
        'file_path': filePath,
        'quality': quality,
        'output_format': outputFormat,
      }),
      (data) => data as Map<String, dynamic>,
    );
  }

  Future<List<Map<String, dynamic>>> getConversions() {
    return _handleResponse(
      _dio.get('/api/conversions'),
      (data) => (data as List).cast<Map<String, dynamic>>(),
    );
  }

  Future<Map<String, dynamic>> getConversion(String id) {
    return _handleResponse(
      _dio.get('/api/conversions/$id'),
      (data) => data as Map<String, dynamic>,
    );
  }

  Future<void> cancelConversion(String id) {
    return _handleResponse(
      _dio.delete('/api/conversions/$id'),
      (_) {},
    );
  }

  // ==========================================================================
  // Config
  // ==========================================================================

  Future<Map<String, dynamic>> getConfig() {
    return _handleResponse(
      _dio.get('/api/config'),
      (data) => data as Map<String, dynamic>,
    );
  }

  Future<Map<String, dynamic>> updateConfig(
    Map<String, dynamic> updates,
  ) {
    return _handleResponse(
      _dio.patch('/api/config', data: updates),
      (data) => data as Map<String, dynamic>,
    );
  }
}

/// API Exception for backend errors
class ApiException implements Exception {
  final String code;
  final String message;

  ApiException({
    required this.code,
    required this.message,
  });

  @override
  String toString() => 'ApiException($code): $message';
}
