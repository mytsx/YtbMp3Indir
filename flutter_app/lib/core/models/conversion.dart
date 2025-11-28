/// Conversion model
class Conversion {
  final String id;
  final String inputPath;
  final String? outputPath;
  final String fileName;
  final String status; // pending, converting, completed, failed, cancelled
  final int progress; // 0-100
  final String? error;
  final DateTime createdAt;
  final double? duration;

  Conversion({
    required this.id,
    required this.inputPath,
    this.outputPath,
    required this.fileName,
    required this.status,
    required this.progress,
    this.error,
    required this.createdAt,
    this.duration,
  });

  factory Conversion.fromJson(Map<String, dynamic> json) {
    return Conversion(
      id: json['id'] as String,
      inputPath: json['input_path'] as String,
      outputPath: json['output_path'] as String?,
      fileName: json['file_name'] as String,
      status: json['status'] as String,
      progress: (json['progress'] as num?)?.toInt() ?? 0,
      error: json['error'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      duration: (json['duration'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'input_path': inputPath,
      'output_path': outputPath,
      'file_name': fileName,
      'status': status,
      'progress': progress,
      'error': error,
      'created_at': createdAt.toIso8601String(),
      'duration': duration,
    };
  }

  Conversion copyWith({
    String? id,
    String? inputPath,
    String? outputPath,
    String? fileName,
    String? status,
    int? progress,
    String? error,
    DateTime? createdAt,
    double? duration,
  }) {
    return Conversion(
      id: id ?? this.id,
      inputPath: inputPath ?? this.inputPath,
      outputPath: outputPath ?? this.outputPath,
      fileName: fileName ?? this.fileName,
      status: status ?? this.status,
      progress: progress ?? this.progress,
      error: error ?? this.error,
      createdAt: createdAt ?? this.createdAt,
      duration: duration ?? this.duration,
    );
  }

  bool get isActive => status == 'converting';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isCancelled => status == 'cancelled';
}

/// Progress update from WebSocket for conversion
class ConversionProgressUpdate {
  final String type; // progress, status, error, completed
  final int? progress;
  final String? status;
  final String? error;
  final String? message;
  final String? outputPath;

  ConversionProgressUpdate({
    required this.type,
    this.progress,
    this.status,
    this.error,
    this.message,
    this.outputPath,
  });

  factory ConversionProgressUpdate.fromJson(Map<String, dynamic> json) {
    return ConversionProgressUpdate(
      type: json['type'] as String,
      progress: (json['progress'] as num?)?.toInt(),
      status: json['status'] as String?,
      error: json['error'] as String?,
      message: json['message'] as String?,
      outputPath: json['output_path'] as String?,
    );
  }
}
