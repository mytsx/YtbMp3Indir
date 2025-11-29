import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../../../core/constants.dart';
import '../../../core/providers/providers.dart';
import '../../../core/models/conversion.dart';
import '../../../shared/widgets/empty_state_widget.dart';
import '../providers/conversion_provider.dart';
import '../widgets/conversion_card.dart';
import '../widgets/file_selection_card.dart';

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

    setState(() {
      _isConverting = true;
      _errorMessage = null;
    });

    try {
      // Call API to start conversion (always use max quality)
      final result = await apiClient.startConversion(
        _selectedFilePath!,
        quality: kDefaultQuality,
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
            FileSelectionCard(
              selectedFilePath: _selectedFilePath,
              selectedFileName: _selectedFileName,
              errorMessage: _errorMessage,
              isConverting: _isConverting,
              onPickFile: _pickFile,
              onClearFile: () {
                setState(() {
                  _selectedFilePath = null;
                  _selectedFileName = null;
                });
              },
              onConvert: _startConversion,
            ),

            const SizedBox(height: 24),

            // Conversions header
            Row(
              children: [
                Text(
                  'Conversions',
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
                  ? const EmptyStateWidget(
                      icon: Icons.transform_outlined,
                      title: 'No conversions yet',
                      subtitle: 'Select a file above to start converting',
                      iconSize: 48,
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
