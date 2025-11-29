import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:desktop_drop/desktop_drop.dart';
import 'package:dotted_border/dotted_border.dart';
import '../../../core/theme/cyberpunk_colors.dart';

class FileSelectionCard extends StatefulWidget {
  final String? selectedFilePath;
  final String? selectedFileName;
  final String selectedFormat;
  final String? errorMessage;
  final bool isConverting;
  final VoidCallback onPickFile;
  final VoidCallback onClearFile;
  final VoidCallback onConvert;
  final Function(String path, String name)? onFileDrop;
  final Function(String format)? onFormatChanged;

  const FileSelectionCard({
    super.key,
    this.selectedFilePath,
    this.selectedFileName,
    this.selectedFormat = 'mp3',
    this.errorMessage,
    required this.isConverting,
    required this.onPickFile,
    required this.onClearFile,
    required this.onConvert,
    this.onFileDrop,
    this.onFormatChanged,
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

  static const _outputFormats = ['mp3', 'wav', 'flac', 'aac', 'ogg'];

  bool _isSupported(String path) {
    final ext = path.split('.').last.toLowerCase();
    return _supportedExtensions.contains(ext);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.white.withValues(alpha: 0.08),
            Colors.white.withValues(alpha: 0.03),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.1),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: CyberpunkColors.hotPink.withValues(alpha: 0.1),
            blurRadius: 20,
            spreadRadius: -5,
          ),
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
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
                            backgroundColor: CyberpunkColors.neonPinkGlow,
                          ),
                        );
                      }
                    }
                  },
                  child: DottedBorder(
                    borderType: BorderType.RRect,
                    radius: const Radius.circular(12),
                    dashPattern: const [8, 4],
                    strokeWidth: _isDragging ? 2 : 1.5,
                    color: _isDragging
                        ? CyberpunkColors.hotPink
                        : widget.selectedFilePath != null
                            ? CyberpunkColors.matrixGreen
                            : CyberpunkColors.surfaceBorder,
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
                      decoration: BoxDecoration(
                        color: _isDragging
                            ? CyberpunkColors.hotPink.withValues(alpha: 0.1)
                            : widget.selectedFilePath != null
                                ? CyberpunkColors.matrixGreen.withValues(alpha: 0.05)
                                : CyberpunkColors.charcoal.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(12),
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
                          ? CyberpunkColors.hotPink
                          : widget.selectedFilePath != null
                              ? CyberpunkColors.matrixGreen
                              : CyberpunkColors.textSecondary,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _isDragging
                          ? 'Drop file here'
                          : widget.selectedFileName ?? 'Drag and drop your file here',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: _isDragging
                            ? CyberpunkColors.hotPink
                            : widget.selectedFilePath != null
                                ? CyberpunkColors.matrixGreen
                                : CyberpunkColors.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    if (widget.selectedFilePath == null && !_isDragging) ...[
                      const SizedBox(height: 8),
                      const Text(
                        'or',
                        style: TextStyle(color: CyberpunkColors.textSecondary),
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
                        style: const TextStyle(
                          fontSize: 12,
                          color: CyberpunkColors.textSecondary,
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
            ),

            if (widget.errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                widget.errorMessage!,
                style: const TextStyle(color: CyberpunkColors.neonPinkGlow, fontSize: 13),
              ),
            ],

            const SizedBox(height: 16),

            // Convert button with format selector
            Row(
              children: [
                // Convert button
                Expanded(
                  child: FilledButton.icon(
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
                    label: Text(widget.isConverting ? 'Converting...' : 'Convert'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      textStyle: const TextStyle(fontSize: 16),
                      backgroundColor: CyberpunkColors.hotPink,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                // Small format selector
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    border: Border.all(color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: widget.selectedFormat,
                      icon: const Icon(Icons.arrow_drop_down, size: 20),
                      isDense: true,
                      focusColor: Colors.transparent,
                      items: _outputFormats.map((format) {
                        return DropdownMenuItem<String>(
                          value: format,
                          child: Text(
                            format.toUpperCase(),
                            style: const TextStyle(fontWeight: FontWeight.w500),
                          ),
                        );
                      }).toList(),
                      onChanged: widget.isConverting
                          ? null
                          : (value) {
                              if (value != null) {
                                widget.onFormatChanged?.call(value);
                              }
                            },
                    ),
                  ),
                ),
              ],
            ),

            // Supported formats
            const SizedBox(height: 12),
            const Text(
              'Input: MP4, MKV, AVI, MOV, WAV, FLAC, AAC, M4A, and more',
              style: TextStyle(
                fontSize: 12,
                color: CyberpunkColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
          ],
            ),
          ),
        ),
      ),
    );
  }
}
