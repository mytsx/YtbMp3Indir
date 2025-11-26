import 'package:flutter_test/flutter_test.dart';
import 'package:mp3yap/core/models/download.dart';
import 'package:mp3yap/core/models/history_item.dart';

void main() {
  group('Download Model', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'test-123',
        'url': 'https://youtube.com/watch?v=abc',
        'status': 'downloading',
        'progress': 50,
        'video_title': 'Test Video',
        'file_path': '/path/to/file.mp3',
        'error': null,
        'created_at': '2024-01-01T12:00:00.000Z',
        'speed': '1.50 MB/s',
        'eta': '00:30',
      };

      final download = Download.fromJson(json);

      expect(download.id, 'test-123');
      expect(download.url, 'https://youtube.com/watch?v=abc');
      expect(download.status, 'downloading');
      expect(download.progress, 50);
      expect(download.videoTitle, 'Test Video');
      expect(download.filePath, '/path/to/file.mp3');
      expect(download.speed, '1.50 MB/s');
      expect(download.eta, '00:30');
    });

    test('isActive returns true for downloading status', () {
      final download = Download(
        id: 'test',
        url: 'https://youtube.com',
        status: 'downloading',
        progress: 50,
        createdAt: DateTime.now(),
      );

      expect(download.isActive, true);
    });

    test('isActive returns true for converting status', () {
      final download = Download(
        id: 'test',
        url: 'https://youtube.com',
        status: 'converting',
        progress: 99,
        createdAt: DateTime.now(),
      );

      expect(download.isActive, true);
    });

    test('isActive returns false for completed status', () {
      final download = Download(
        id: 'test',
        url: 'https://youtube.com',
        status: 'completed',
        progress: 100,
        createdAt: DateTime.now(),
      );

      expect(download.isActive, false);
    });

    test('copyWith updates fields correctly', () {
      final original = Download(
        id: 'test',
        url: 'https://youtube.com',
        status: 'pending',
        progress: 0,
        createdAt: DateTime.now(),
      );

      final updated = original.copyWith(
        status: 'downloading',
        progress: 50,
        speed: '2.00 MB/s',
        eta: '01:00',
        videoTitle: 'Updated Title',
      );

      expect(updated.id, 'test'); // unchanged
      expect(updated.status, 'downloading');
      expect(updated.progress, 50);
      expect(updated.speed, '2.00 MB/s');
      expect(updated.eta, '01:00');
      expect(updated.videoTitle, 'Updated Title');
    });
  });

  group('ProgressUpdate Model', () {
    test('fromJson parses progress type', () {
      final json = {
        'type': 'progress',
        'progress': 75,
        'speed': '3.50 MB/s',
        'eta': '00:15',
      };

      final update = ProgressUpdate.fromJson(json);

      expect(update.type, 'progress');
      expect(update.progress, 75);
      expect(update.speed, '3.50 MB/s');
      expect(update.eta, '00:15');
    });

    test('fromJson parses status type with all fields', () {
      final json = {
        'type': 'status',
        'status': 'downloading',
        'progress': 25,
        'speed': '1.00 MB/s',
        'eta': '02:00',
        'video_title': 'Test Video',
      };

      final update = ProgressUpdate.fromJson(json);

      expect(update.type, 'status');
      expect(update.status, 'downloading');
      expect(update.progress, 25);
      expect(update.speed, '1.00 MB/s');
      expect(update.eta, '02:00');
      expect(update.videoTitle, 'Test Video');
    });

    test('fromJson parses completed type', () {
      final json = {
        'type': 'completed',
        'status': 'completed',
        'progress': 100,
        'file_path': '/path/to/file.mp3',
        'message': 'Download completed!',
      };

      final update = ProgressUpdate.fromJson(json);

      expect(update.type, 'completed');
      expect(update.progress, 100);
      expect(update.filePath, '/path/to/file.mp3');
      expect(update.message, 'Download completed!');
    });

    test('fromJson parses error type', () {
      final json = {
        'type': 'error',
        'status': 'failed',
        'error': 'Network error',
        'message': 'Download failed: Network error',
      };

      final update = ProgressUpdate.fromJson(json);

      expect(update.type, 'error');
      expect(update.status, 'failed');
      expect(update.error, 'Network error');
    });
  });

  group('HistoryItem Model', () {
    test('formattedSize shows 1 decimal for MB', () {
      final item = HistoryItem(
        id: 1,
        videoTitle: 'Test',
        fileName: 'test.mp3',
        format: 'mp3',
        url: 'https://youtube.com',
        fileSize: 5242880, // 5 MB
        downloadedAt: DateTime.now(),
        status: 'completed',
      );

      expect(item.formattedSize, '5.0 MB');
    });

    test('formattedSize shows 1 decimal for KB', () {
      final item = HistoryItem(
        id: 1,
        videoTitle: 'Test',
        fileName: 'test.mp3',
        format: 'mp3',
        url: 'https://youtube.com',
        fileSize: 512000, // ~500 KB
        downloadedAt: DateTime.now(),
        status: 'completed',
      );

      expect(item.formattedSize, '500.0 KB');
    });

    test('formattedSize shows N/A for null', () {
      final item = HistoryItem(
        id: 1,
        videoTitle: 'Test',
        fileName: 'test.mp3',
        format: 'mp3',
        url: 'https://youtube.com',
        fileSize: null,
        downloadedAt: DateTime.now(),
        status: 'completed',
      );

      expect(item.formattedSize, 'N/A');
    });

    test('formattedDuration formats correctly', () {
      final item = HistoryItem(
        id: 1,
        videoTitle: 'Test',
        fileName: 'test.mp3',
        format: 'mp3',
        url: 'https://youtube.com',
        duration: 185, // 3:05
        downloadedAt: DateTime.now(),
        status: 'completed',
      );

      expect(item.formattedDuration, '03:05');
    });

    test('formattedDate shows Just now for recent', () {
      final item = HistoryItem(
        id: 1,
        videoTitle: 'Test',
        fileName: 'test.mp3',
        format: 'mp3',
        url: 'https://youtube.com',
        downloadedAt: DateTime.now(),
        status: 'completed',
      );

      expect(item.formattedDate, 'Just now');
    });
  });
}
