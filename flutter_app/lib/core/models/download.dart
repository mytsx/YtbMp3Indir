/// Download model
class Download {
  final String id;
  final String url;
  final String status; // pending, downloading, converting, completed, failed, cancelled
  final int progress; // 0-100
  final String? videoTitle;
  final String? filePath;
  final String? error;
  final DateTime createdAt;
  final String? speed;
  final String? eta;

  Download({
    required this.id,
    required this.url,
    required this.status,
    required this.progress,
    this.videoTitle,
    this.filePath,
    this.error,
    required this.createdAt,
    this.speed,
    this.eta,
  });

  factory Download.fromJson(Map<String, dynamic> json) {
    return Download(
      id: json['id'] as String,
      url: json['url'] as String,
      status: json['status'] as String,
      progress: (json['progress'] as num?)?.toInt() ?? 0,
      videoTitle: json['video_title'] as String?,
      filePath: json['file_path'] as String?,
      error: json['error'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      speed: json['speed'] as String?,
      eta: json['eta'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'url': url,
      'status': status,
      'progress': progress,
      'video_title': videoTitle,
      'file_path': filePath,
      'error': error,
      'created_at': createdAt.toIso8601String(),
      'speed': speed,
      'eta': eta,
    };
  }

  Download copyWith({
    String? id,
    String? url,
    String? status,
    int? progress,
    String? videoTitle,
    String? filePath,
    String? error,
    DateTime? createdAt,
    String? speed,
    String? eta,
  }) {
    return Download(
      id: id ?? this.id,
      url: url ?? this.url,
      status: status ?? this.status,
      progress: progress ?? this.progress,
      videoTitle: videoTitle ?? this.videoTitle,
      filePath: filePath ?? this.filePath,
      error: error ?? this.error,
      createdAt: createdAt ?? this.createdAt,
      speed: speed ?? this.speed,
      eta: eta ?? this.eta,
    );
  }

  bool get isActive => status == 'downloading' || status == 'converting';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isCancelled => status == 'cancelled';
}

/// Progress update from WebSocket
class ProgressUpdate {
  final String type; // progress, status, error, completed, info
  final int? progress;
  final String? speed;
  final String? eta;
  final String? status;
  final String? error;
  final String? message;
  final String? videoTitle;
  final String? filePath;

  ProgressUpdate({
    required this.type,
    this.progress,
    this.speed,
    this.eta,
    this.status,
    this.error,
    this.message,
    this.videoTitle,
    this.filePath,
  });

  factory ProgressUpdate.fromJson(Map<String, dynamic> json) {
    return ProgressUpdate(
      type: json['type'] as String,
      progress: (json['progress'] as num?)?.toInt(),
      speed: json['speed'] as String?,
      eta: json['eta'] as String?,
      status: json['status'] as String?,
      error: json['error'] as String?,
      message: json['message'] as String?,
      videoTitle: json['video_title'] as String?,
      filePath: json['file_path'] as String?,
    );
  }
}
