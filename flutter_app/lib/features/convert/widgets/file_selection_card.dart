import 'package:flutter/material.dart';

class FileSelectionCard extends StatelessWidget {
  final String? selectedFilePath;
  final String? selectedFileName;
  final String? errorMessage;
  final bool isConverting;
  final VoidCallback onPickFile;
  final VoidCallback onClearFile;
  final VoidCallback onConvert;

  const FileSelectionCard({
    super.key,
    this.selectedFilePath,
    this.selectedFileName,
    this.errorMessage,
    required this.isConverting,
    required this.onPickFile,
    required this.onClearFile,
    required this.onConvert,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // File picker button
            OutlinedButton.icon(
              onPressed: onPickFile,
              icon: const Icon(Icons.folder_open),
              label: Text(
                selectedFileName ?? 'Select a video or audio file',
              ),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  vertical: 20,
                  horizontal: 16,
                ),
                side: BorderSide(
                  color: selectedFilePath != null
                      ? Colors.green
                      : Colors.grey.shade400,
                  width: selectedFilePath != null ? 2 : 1,
                ),
              ),
            ),

            if (selectedFilePath != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.check_circle,
                      color: Colors.green.shade700,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        selectedFilePath!,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.green.shade800,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 18),
                      onPressed: onClearFile,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
              ),
            ],

            if (errorMessage != null) ...[
              const SizedBox(height: 12),
              Text(
                errorMessage!,
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 13,
                ),
              ),
            ],

            const SizedBox(height: 16),

            // Convert button
            FilledButton.icon(
              onPressed:
                  isConverting || selectedFilePath == null ? null : onConvert,
              icon: isConverting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.transform),
              label: Text(
                isConverting ? 'Converting...' : 'Convert to MP3',
              ),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 16),
                backgroundColor: Colors.orange,
              ),
            ),

            // Tips
            const SizedBox(height: 12),
            Text(
              'Supported: MP4, MKV, AVI, MOV, WAV, FLAC, AAC, and more',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
