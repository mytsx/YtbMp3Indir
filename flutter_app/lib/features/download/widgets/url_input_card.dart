import 'package:flutter/material.dart';

class UrlInputCard extends StatelessWidget {
  final TextEditingController controller;
  final bool isDownloading;
  final String? errorMessage;
  final VoidCallback onDownloadPressed;

  const UrlInputCard({
    super.key,
    required this.controller,
    required this.isDownloading,
    this.errorMessage,
    required this.onDownloadPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // URL TextField
            TextField(
              controller: controller,
              decoration: InputDecoration(
                labelText: 'YouTube URL',
                hintText: 'https://youtube.com/watch?v=...',
                prefixIcon: const Icon(Icons.link),
                errorText: errorMessage,
              ),
              maxLines: 1,
              textInputAction: TextInputAction.done,
              onSubmitted: (_) => onDownloadPressed(),
            ),
            const SizedBox(height: 16),

            // Download button
            FilledButton.icon(
              onPressed: isDownloading ? null : onDownloadPressed,
              icon: isDownloading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.download),
              label: Text(isDownloading ? 'Starting...' : 'Start Download'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 16),
              ),
            ),

            // Tips
            const SizedBox(height: 12),
            Text(
              'Tip: You can download individual videos or entire playlists',
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
