import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../../../core/providers/providers.dart';
import '../../../core/models/conversion.dart';
import '../providers/conversion_provider.dart';
import '../widgets/conversion_card.dart';

/// Main convert screen for local file to MP3 conversion
class ConvertScreen extends ConsumerStatefulWidget {
  const ConvertScreen({super.key});

  @override
  ConsumerState<ConvertScreen> createState() => _ConvertScreenState();
}

class _ConvertScreenState extends ConsumerState<ConvertScreen> {
  String? _selectedFilePath;
  String? _selectedFileName;
  bool _isConverting = false;
  String? _errorMessage;
  String _selectedQuality = '192';

  final List<String> _qualityOptions = ['128', '192', '256', '320'];

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: [
          // Video formats
          'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v',
          // Audio formats
          'wav', 'flac', 'aac', 'm4a', 'ogg', 'wma', 'aiff',
        ],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        setState(() {
          _selectedFilePath = file.path;
          _selectedFileName = file.name;
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to pick file: $e';
      });
    }
  }

  Future<void> _startConversion() async {
    if (_selectedFilePath == null) {
      setState(() {
        _errorMessage = 'Please select a file first';
      });
      return;
    }

    final apiClient = ref.read(apiClientProvider);
    if (apiClient == null) {
      setState(() {
        _errorMessage = 'Backend not ready. Please wait...';
      });
      return;
    }

    setState(() {
      _isConverting = true;
      _errorMessage = null;
    });

    try {
      // Call API to start conversion
      final result = await apiClient.startConversion(
        _selectedFilePath!,
        quality: _selectedQuality,
      );

      // Parse response to Conversion model
      final conversion = Conversion.fromJson(result);

      // Add to conversions list
      ref.read(conversionsProvider.notifier).addConversion(conversion);

      // Clear selection on success
      setState(() {
        _selectedFilePath = null;
        _selectedFileName = null;
      });

      // Show success snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Conversion started!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to start conversion: $e';
      });

      // Show error snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isConverting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Watch conversions list
    final conversions = ref.watch(conversionsProvider);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // File selection section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // File picker button
                    OutlinedButton.icon(
                      onPressed: _pickFile,
                      icon: const Icon(Icons.folder_open),
                      label: Text(
                        _selectedFileName ?? 'Select a video or audio file',
                      ),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          vertical: 20,
                          horizontal: 16,
                        ),
                        side: BorderSide(
                          color: _selectedFilePath != null
                              ? Colors.green
                              : Colors.grey.shade400,
                          width: _selectedFilePath != null ? 2 : 1,
                        ),
                      ),
                    ),

                    if (_selectedFilePath != null) ...[
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
                                _selectedFilePath!,
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
                              onPressed: () {
                                setState(() {
                                  _selectedFilePath = null;
                                  _selectedFileName = null;
                                });
                              },
                              padding: EdgeInsets.zero,
                              constraints: const BoxConstraints(),
                            ),
                          ],
                        ),
                      ),
                    ],

                    const SizedBox(height: 16),

                    // Quality selector
                    Row(
                      children: [
                        const Text(
                          'Quality:',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: SegmentedButton<String>(
                            segments: _qualityOptions
                                .map((q) => ButtonSegment<String>(
                                      value: q,
                                      label: Text('$q kbps'),
                                    ))
                                .toList(),
                            selected: {_selectedQuality},
                            onSelectionChanged: (selected) {
                              setState(() {
                                _selectedQuality = selected.first;
                              });
                            },
                          ),
                        ),
                      ],
                    ),

                    if (_errorMessage != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        _errorMessage!,
                        style: const TextStyle(
                          color: Colors.red,
                          fontSize: 13,
                        ),
                      ),
                    ],

                    const SizedBox(height: 16),

                    // Convert button
                    FilledButton.icon(
                      onPressed: _isConverting || _selectedFilePath == null
                          ? null
                          : _startConversion,
                      icon: _isConverting
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.transform),
                      label: Text(
                        _isConverting ? 'Converting...' : 'Convert to MP3',
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
            ),

            const SizedBox(height: 24),

            // Conversions header
            Row(
              children: [
                Text(
                  'Active Conversions',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(width: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${conversions.length}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.orange.shade900,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Conversions list
            Expanded(
              child: conversions.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.transform_outlined,
                            size: 48,
                            color: Colors.grey.shade300,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'No conversions yet',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey.shade600,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Select a file above to convert to MP3',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade500,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      itemCount: conversions.length,
                      itemBuilder: (context, index) {
                        final conversion = conversions[index];
                        return ConversionCard(conversion: conversion);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
