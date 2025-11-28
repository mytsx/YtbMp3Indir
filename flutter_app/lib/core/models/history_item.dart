/// History item model representing a completed download
class HistoryItem {
  final int id;
  final String videoTitle;
  final String fileName;
  final String? filePath;
  final String format;
  final String url;
  final int? fileSize;
  final int? duration;
  final String? channelName;
  final String? channelUrl;
  final String? videoId;
  final DateTime downloadedAt;
  final String status;

  const HistoryItem({
    required this.id,
    required this.videoTitle,
    required this.fileName,
    this.filePath,
    required this.format,
    required this.url,
    this.fileSize,
    this.duration,
    this.channelName,
    this.channelUrl,
    this.videoId,
    required this.downloadedAt,
    required this.status,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id'] as int,
      videoTitle: json['video_title'] as String,
      fileName: json['file_name'] as String,
      filePath: json['file_path'] as String?,
      format: json['format'] as String? ?? 'mp3',
      url: json['url'] as String,
      fileSize: json['file_size'] as int?,
      duration: json['duration'] as int?,
      channelName: json['channel_name'] as String?,
      channelUrl: json['channel_url'] as String?,
      videoId: json['video_id'] as String?,
      downloadedAt: DateTime.parse(json['downloaded_at'] as String),
      status: json['status'] as String? ?? 'completed',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'video_title': videoTitle,
      'file_name': fileName,
      'file_path': filePath,
      'format': format,
      'url': url,
      'file_size': fileSize,
      'duration': duration,
      'channel_name': channelName,
      'channel_url': channelUrl,
      'video_id': videoId,
      'downloaded_at': downloadedAt.toIso8601String(),
      'status': status,
    };
  }

  /// Format file size for display
  String get formattedSize {
    if (fileSize == null) return 'N/A';
    final size = fileSize!;
    if (size < 1024) return '$size B';
    if (size < 1024 * 1024) return '${(size / 1024).toStringAsFixed(1)} KB';
    return '${(size / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  /// Format duration for display
  String get formattedDuration {
    if (duration == null) return 'N/A';
    final d = duration!;
    final minutes = d ~/ 60;
    final seconds = d % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  /// Format downloaded date for display
  String get formattedDate {
    final now = DateTime.now();
    final diff = now.difference(downloadedAt);

    if (diff.inDays == 0) {
      if (diff.inHours == 0) {
        if (diff.inMinutes == 0) return 'Just now';
        return '${diff.inMinutes}m ago';
      }
      return '${diff.inHours}h ago';
    }
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays} days ago';

    return '${downloadedAt.day}/${downloadedAt.month}/${downloadedAt.year}';
  }
}

/// Download statistics model
class DownloadStats {
  final int totalDownloads;
  final int totalSize;
  final int totalDuration;

  const DownloadStats({
    required this.totalDownloads,
    required this.totalSize,
    required this.totalDuration,
  });

  factory DownloadStats.fromJson(Map<String, dynamic> json) {
    return DownloadStats(
      totalDownloads: json['total_downloads'] as int? ?? 0,
      totalSize: json['total_size'] as int? ?? 0,
      totalDuration: json['total_duration'] as int? ?? 0,
    );
  }

  /// Format total size for display
  String get formattedSize {
    if (totalSize < 1024) return '$totalSize B';
    if (totalSize < 1024 * 1024) return '${(totalSize / 1024).toStringAsFixed(1)} KB';
    if (totalSize < 1024 * 1024 * 1024) {
      return '${(totalSize / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(totalSize / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
  }

  /// Format total duration for display
  String get formattedDuration {
    final hours = totalDuration ~/ 3600;
    final minutes = (totalDuration % 3600) ~/ 60;

    if (hours > 0) {
      return '${hours}h ${minutes}m';
    }
    return '${minutes}m';
  }
}
