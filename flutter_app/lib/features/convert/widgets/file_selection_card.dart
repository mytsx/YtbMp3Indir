import 'package:flutter/material.dart';
import 'package:desktop_drop/desktop_drop.dart';

class FileSelectionCard extends StatefulWidget {
  final String? selectedFilePath;
  final String? selectedFileName;
  final String? errorMessage;
  final bool isConverting;
  final VoidCallback onPickFile;
  final VoidCallback onClearFile;
  final VoidCallback onConvert;
  final Function(String path, String name)? onFileDrop;

  const FileSelectionCard({
    super.key,
    this.selectedFilePath,
    this.selectedFileName,
    this.errorMessage,
    required this.isConverting,
    required this.onPickFile,
    required this.onClearFile,
    required this.onConvert,
    this.onFileDrop,
  });

  @override
  State<FileSelectionCard> createState() => _FileSelectionCardState();
}

class _FileSelectionCardState extends State<FileSelectionCard> {
  bool _isDragging = false;

  static const _supportedExtensions = [
    // Video
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v',
    // Audio
    'wav', 'flac', 'aac', 'm4a', 'ogg', 'wma', 'aiff',
  ];

  bool _isSupported(String path) {
    final ext = path.split('.').last.toLowerCase();
    return _supportedExtensions.contains(ext);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Drag & Drop Zone
            DropTarget(
              onDragEntered: (_) => setState(() => _isDragging = true),
              onDragExited: (_) => setState(() => _isDragging = false),
              onDragDone: (details) {
                setState(() => _isDragging = false);
                if (details.files.isNotEmpty) {
                  final file = details.files.first;
                  if (_isSupported(file.path)) {
                    widget.onFileDrop?.call(file.path, file.name);
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Unsupported file format'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                }
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
                decoration: BoxDecoration(
                  color: _isDragging
                      ? colorScheme.primaryContainer.withValues(alpha: 0.3)
                      : colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _isDragging
                        ? colorScheme.primary
                        : widget.selectedFilePath != null
                            ? Colors.green
                            : colorScheme.outline.withValues(alpha: 0.5),
                    width: _isDragging ? 2 : 1,
                    strokeAlign: BorderSide.strokeAlignInside,
                  ),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _isDragging
                          ? Icons.file_download
                          : widget.selectedFilePath != null
                              ? Icons.check_circle
                              : Icons.cloud_upload_outlined,
                      size: 48,
                      color: _isDragging
                          ? colorScheme.primary
                          : widget.selectedFilePath != null
                              ? Colors.green
                              : colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _isDragging
                          ? 'Drop file here'
                          : widget.selectedFileName ?? 'Drag and drop your file here',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: _isDragging
                            ? colorScheme.primary
                            : widget.selectedFilePath != null
                                ? Colors.green.shade700
                                : colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    if (widget.selectedFilePath == null && !_isDragging) ...[
                      const SizedBox(height: 8),
                      Text(
                        'or',
                        style: TextStyle(color: colorScheme.onSurfaceVariant),
                      ),
                      const SizedBox(height: 8),
                      OutlinedButton(
                        onPressed: widget.onPickFile,
                        child: const Text('Browse Files'),
                      ),
                    ],
                    if (widget.selectedFilePath != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        widget.selectedFilePath!,
                        style: TextStyle(
                          fontSize: 12,
                          color: colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          TextButton.icon(
                            onPressed: widget.onClearFile,
                            icon: const Icon(Icons.close, size: 18),
                            label: const Text('Clear'),
                          ),
                          const SizedBox(width: 16),
                          TextButton.icon(
                            onPressed: widget.onPickFile,
                            icon: const Icon(Icons.folder_open, size: 18),
                            label: const Text('Change'),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),

            if (widget.errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                widget.errorMessage!,
                style: const TextStyle(color: Colors.red, fontSize: 13),
              ),
            ],

            const SizedBox(height: 16),

            // Convert button
            FilledButton.icon(
              onPressed: widget.isConverting || widget.selectedFilePath == null
                  ? null
                  : widget.onConvert,
              icon: widget.isConverting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.transform),
              label: Text(widget.isConverting ? 'Converting...' : 'Convert to MP3'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 16),
                backgroundColor: Colors.orange,
              ),
            ),

            // Supported formats
            const SizedBox(height: 12),
            Text(
              'Supported: MP4, MKV, AVI, MOV, WAV, FLAC, AAC, M4A, and more',
              style: TextStyle(
                fontSize: 12,
                color: colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
