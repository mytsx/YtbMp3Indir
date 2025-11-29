import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:easy_localization/easy_localization.dart';
import '../../../core/constants.dart';
import '../../../core/providers/providers.dart';
import '../../../core/models/conversion.dart';
import '../../../core/theme/cyberpunk_colors.dart';
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
  String _selectedFormat = 'mp3';
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
        _errorMessage = 'convert.error_pick_file'.tr(args: [e.toString()]);
      });
    }
  }

  Future<void> _startConversion() async {
    if (_selectedFilePath == null) {
      setState(() {
        _errorMessage = 'convert.error_select_file'.tr();
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
        outputFormat: _selectedFormat,
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
          SnackBar(
            content: Text('convert.snackbar_started'.tr()),
            backgroundColor: CyberpunkColors.matrixGreen,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'convert.error_start'.tr(args: [e.toString()]);
      });

      // Show error snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('convert.snackbar_error'.tr(args: [e.toString()])),
            backgroundColor: CyberpunkColors.neonPinkGlow,
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
    final themeStyle = ref.watch(themeStyleProvider);
    final isCyberpunk = themeStyle == 'cyberpunk';
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: (isCyberpunk && isDarkMode) ? Colors.transparent : null,
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // File selection section
            FileSelectionCard(
              selectedFilePath: _selectedFilePath,
              selectedFileName: _selectedFileName,
              selectedFormat: _selectedFormat,
              errorMessage: _errorMessage,
              isConverting: _isConverting,
              onPickFile: _pickFile,
              onClearFile: () {
                setState(() {
                  _selectedFilePath = null;
                  _selectedFileName = null;
                  _errorMessage = null;
                });
              },
              onConvert: _startConversion,
              onFileDrop: (path, name) {
                setState(() {
                  _selectedFilePath = path;
                  _selectedFileName = name;
                  _errorMessage = null;
                });
              },
              onFormatChanged: (format) {
                setState(() {
                  _selectedFormat = format;
                });
              },
            ),

            const SizedBox(height: 24),

            // Conversions header
            Row(
              children: [
                Text(
                  'convert.title'.tr(),
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
                    color: isCyberpunk
                        ? CyberpunkColors.cyberYellow.withValues(alpha: 0.2)
                        : colorScheme.tertiaryContainer,
                    borderRadius: BorderRadius.circular(12),
                    border: isCyberpunk
                        ? Border.all(
                            color: CyberpunkColors.cyberYellow
                                .withValues(alpha: 0.5),
                            width: 1,
                          )
                        : null,
                  ),
                  child: Text(
                    '${conversions.length}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isCyberpunk
                          ? CyberpunkColors.cyberYellow
                          : colorScheme.onTertiaryContainer,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Conversions list
            Expanded(
              child: conversions.isEmpty
                  ? EmptyStateWidget(
                      icon: Icons.transform_outlined,
                      title: 'convert.empty_list'.tr(),
                      subtitle: 'convert.empty_subtitle'.tr(),
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
