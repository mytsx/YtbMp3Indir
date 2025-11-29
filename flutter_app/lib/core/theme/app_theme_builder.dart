import 'package:flutter/material.dart';
import 'safe_google_fonts.dart';

/// A builder class that constructs a consistent [ThemeData] based on a given [ColorScheme].
///
/// This class enforces the DRY principle by defining component styles (Buttons, Inputs, Cards)
/// in a single place, parameterized by the color scheme. This ensures that all themes
/// (Light, Dark, Cyberpunk, etc.) share the same structural design language while
/// differing only in colors and typography.
class AppThemeBuilder {
  const AppThemeBuilder._();

  /// Builds a complete [ThemeData] using the provided colors and text theme.
  static ThemeData build({
    required ColorScheme colorScheme,
    required TextTheme textTheme,
    required Color scaffoldBackgroundColor,
  }) {
    final base = colorScheme.brightness == Brightness.dark
        ? ThemeData.dark(useMaterial3: true)
        : ThemeData.light(useMaterial3: true);

    return base.copyWith(
      scaffoldBackgroundColor: scaffoldBackgroundColor,
      colorScheme: colorScheme,
      textTheme: textTheme,
      appBarTheme: _buildAppBarTheme(colorScheme, textTheme),
      cardTheme: _buildCardTheme(colorScheme),
      elevatedButtonTheme: _buildElevatedButtonTheme(colorScheme),
      filledButtonTheme: _buildFilledButtonTheme(colorScheme),
      outlinedButtonTheme: _buildOutlinedButtonTheme(colorScheme),
      textButtonTheme: _buildTextButtonTheme(colorScheme),
      inputDecorationTheme: _buildInputDecorationTheme(colorScheme),
      snackBarTheme: _buildSnackBarTheme(colorScheme),
      progressIndicatorTheme: _buildProgressIndicatorTheme(colorScheme),
      dividerTheme: _buildDividerTheme(colorScheme),
      iconTheme: _buildIconTheme(colorScheme),
      dropdownMenuTheme: _buildDropdownMenuTheme(colorScheme),
      radioTheme: _buildRadioTheme(colorScheme),
      listTileTheme: _buildListTileTheme(colorScheme),
    );
  }

  static AppBarTheme _buildAppBarTheme(
      ColorScheme colors, TextTheme textTheme) {
    return AppBarTheme(
      backgroundColor: colors.brightness == Brightness.dark
          ? Colors.transparent
          : colors.surface,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: SafeGoogleFonts.orbitron(
        20,
        weight: FontWeight.w600,
        color: colors.onSurface,
        letterSpacing: 1,
      ),
      iconTheme: IconThemeData(color: colors.primary),
    );
  }

  static CardThemeData _buildCardTheme(ColorScheme colors) {
    final isDark = colors.brightness == Brightness.dark;
    return CardThemeData(
      color: isDark ? colors.surfaceContainer : colors.surface,
      elevation: isDark ? 0 : 2,
      shadowColor: isDark ? null : colors.primary.withValues(alpha: 0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isDark
              ? colors.outline.withValues(alpha: 0.5)
              : colors.primary.withValues(alpha: 0.2),
          width: 1,
        ),
      ),
      margin: const EdgeInsets.symmetric(vertical: 8),
    );
  }

  static ElevatedButtonThemeData _buildElevatedButtonTheme(ColorScheme colors) {
    return ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: colors.primary,
        foregroundColor: colors.onPrimary,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: SafeGoogleFonts.inter(14, weight: FontWeight.w600),
      ),
    );
  }

  static FilledButtonThemeData _buildFilledButtonTheme(ColorScheme colors) {
    return FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: colors.primary,
        foregroundColor: colors.onPrimary,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: SafeGoogleFonts.inter(14, weight: FontWeight.w600),
      ),
    );
  }

  static OutlinedButtonThemeData _buildOutlinedButtonTheme(ColorScheme colors) {
    return OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: colors.secondary,
        side: BorderSide(color: colors.secondary, width: 1.5),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: SafeGoogleFonts.inter(14, weight: FontWeight.w600),
      ),
    );
  }

  static TextButtonThemeData _buildTextButtonTheme(ColorScheme colors) {
    return TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: colors.secondary,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        textStyle: SafeGoogleFonts.inter(14, weight: FontWeight.w500),
      ),
    );
  }

  static InputDecorationTheme _buildInputDecorationTheme(ColorScheme colors) {
    final isDark = colors.brightness == Brightness.dark;
    final borderColor = isDark
        ? colors.outline.withValues(alpha: 0.5)
        : colors.primary.withValues(alpha: 0.3);
    final fillColor = isDark ? colors.surfaceContainerHighest : colors.surface;

    return InputDecorationTheme(
      filled: true,
      fillColor: fillColor,
      isDense: false,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: borderColor),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: borderColor),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: colors.secondary,
          width: 2,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: colors.error,
          width: 1,
        ),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: colors.error,
          width: 2,
        ),
      ),
      labelStyle: SafeGoogleFonts.inter(14,
          weight: FontWeight.normal, color: colors.onSurfaceVariant),
      floatingLabelStyle: SafeGoogleFonts.inter(14,
          weight: FontWeight.w500, color: colors.secondary),
      hintStyle: SafeGoogleFonts.inter(14,
          weight: FontWeight.normal, color: colors.onSurfaceVariant),
      errorStyle: SafeGoogleFonts.inter(12,
          weight: FontWeight.normal, color: colors.error),
      helperStyle: SafeGoogleFonts.inter(12,
          weight: FontWeight.normal, color: colors.onSurfaceVariant),
      prefixIconColor: colors.secondary,
      suffixIconColor: colors.onSurfaceVariant,
    );
  }

  static SnackBarThemeData _buildSnackBarTheme(ColorScheme colors) {
    return SnackBarThemeData(
      backgroundColor: colors.surfaceContainerHighest,
      contentTextStyle: SafeGoogleFonts.inter(14,
          weight: FontWeight.normal, color: colors.onSurface),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: colors.outline.withValues(alpha: 0.5),
        ),
      ),
      behavior: SnackBarBehavior.floating,
    );
  }

  static ProgressIndicatorThemeData _buildProgressIndicatorTheme(
      ColorScheme colors) {
    return ProgressIndicatorThemeData(
      color: colors.primary,
      linearTrackColor: colors.surfaceContainerHighest,
      circularTrackColor: colors.surfaceContainerHighest,
    );
  }

  static DividerThemeData _buildDividerTheme(ColorScheme colors) {
    return DividerThemeData(
      color: colors.brightness == Brightness.dark
          ? colors.outline.withValues(alpha: 0.5)
          : colors.primary.withValues(alpha: 0.2),
      thickness: 1,
      space: 24,
    );
  }

  static IconThemeData _buildIconTheme(ColorScheme colors) {
    return IconThemeData(
      color: colors.onSurfaceVariant,
      size: 24,
    );
  }

  static DropdownMenuThemeData _buildDropdownMenuTheme(ColorScheme colors) {
    return DropdownMenuThemeData(
      menuStyle: MenuStyle(
        backgroundColor: WidgetStateProperty.all(
            colors.brightness == Brightness.dark
                ? colors.surfaceContainerHighest
                : colors.surface),
        shape: WidgetStateProperty.all(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: colors.brightness == Brightness.dark
                  ? colors.outline.withValues(alpha: 0.5)
                  : colors.primary.withValues(alpha: 0.2),
            ),
          ),
        ),
      ),
    );
  }

  static RadioThemeData _buildRadioTheme(ColorScheme colors) {
    return RadioThemeData(
      fillColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colors.primary;
        }
        return colors.onSurfaceVariant;
      }),
      overlayColor: WidgetStateProperty.all(
        colors.primary.withValues(alpha: 0.1),
      ),
    );
  }

  static ListTileThemeData _buildListTileTheme(ColorScheme colors) {
    return ListTileThemeData(
      iconColor: colors.onSurfaceVariant,
      textColor: colors.onSurface,
      titleTextStyle: SafeGoogleFonts.inter(16,
          weight: FontWeight.normal, color: colors.onSurface),
      subtitleTextStyle: SafeGoogleFonts.inter(14,
          weight: FontWeight.normal, color: colors.onSurfaceVariant),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
    );
  }
}
