import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'cyberpunk_colors.dart';

/// Cyberpunk Design System - Theme Configuration
class CyberpunkTheme {
  CyberpunkTheme._();

  /// Dark theme (primary - this design is dark-mode only)
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: CyberpunkColors.deepSpace,
      colorScheme: _colorScheme,
      textTheme: _textTheme,
      appBarTheme: _appBarTheme,
      cardTheme: _cardTheme,
      elevatedButtonTheme: _elevatedButtonTheme,
      filledButtonTheme: _filledButtonTheme,
      outlinedButtonTheme: _outlinedButtonTheme,
      textButtonTheme: _textButtonTheme,
      inputDecorationTheme: _inputDecorationTheme,
      snackBarTheme: _snackBarTheme,
      progressIndicatorTheme: _progressIndicatorTheme,
      dividerTheme: _dividerTheme,
      iconTheme: _iconTheme,
      dropdownMenuTheme: _dropdownMenuTheme,
    );
  }

  /// Light theme (fallback - minimal styling)
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: CyberpunkColors.electricPurple,
        brightness: Brightness.light,
      ),
      textTheme: _textTheme,
    );
  }

  // === Color Scheme ===
  static const ColorScheme _colorScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: CyberpunkColors.hotPink,
    onPrimary: Colors.white,
    primaryContainer: CyberpunkColors.electricPurple,
    onPrimaryContainer: Colors.white,
    secondary: CyberpunkColors.neonCyan,
    onSecondary: CyberpunkColors.deepSpace,
    secondaryContainer: CyberpunkColors.darkNavy,
    onSecondaryContainer: CyberpunkColors.neonCyan,
    tertiary: CyberpunkColors.electricBlue,
    onTertiary: Colors.white,
    tertiaryContainer: CyberpunkColors.midnightPurple,
    onTertiaryContainer: CyberpunkColors.iceBlue,
    error: CyberpunkColors.neonPinkGlow,
    onError: Colors.white,
    errorContainer: Color(0xFF3D0A1A),
    onErrorContainer: CyberpunkColors.neonPinkGlow,
    surface: CyberpunkColors.deepSpace,
    onSurface: CyberpunkColors.textPrimary,
    surfaceContainerHighest: CyberpunkColors.charcoal,
    onSurfaceVariant: CyberpunkColors.textSecondary,
    outline: CyberpunkColors.surfaceBorder,
    outlineVariant: CyberpunkColors.surfaceBorder,
    shadow: Colors.black,
    scrim: Colors.black,
    inverseSurface: CyberpunkColors.textPrimary,
    onInverseSurface: CyberpunkColors.deepSpace,
    inversePrimary: CyberpunkColors.electricPurple,
  );

  // === Text Theme with Custom Fonts ===
  static TextTheme get _textTheme {
    // Use Orbitron for display/headlines (futuristic)
    // Use Inter for body text (readable)
    return TextTheme(
      // Display - Orbitron (futuristic, used sparingly)
      displayLarge: GoogleFonts.orbitron(
        fontSize: 48,
        fontWeight: FontWeight.bold,
        letterSpacing: 2,
        color: CyberpunkColors.textPrimary,
      ),
      displayMedium: GoogleFonts.orbitron(
        fontSize: 36,
        fontWeight: FontWeight.bold,
        letterSpacing: 1.5,
        color: CyberpunkColors.textPrimary,
      ),
      displaySmall: GoogleFonts.orbitron(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        letterSpacing: 1,
        color: CyberpunkColors.textPrimary,
      ),
      // Headlines - Rajdhani (tech-inspired but readable)
      headlineLarge: GoogleFonts.rajdhani(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
      ),
      headlineMedium: GoogleFonts.rajdhani(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
      ),
      headlineSmall: GoogleFonts.rajdhani(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
      ),
      // Titles - Inter (clean, professional)
      titleLarge: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
      ),
      titleMedium: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
      ),
      titleSmall: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
      ),
      // Body - Inter (excellent readability)
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: CyberpunkColors.textPrimary,
      ),
      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: CyberpunkColors.textPrimary,
      ),
      bodySmall: GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.normal,
        color: CyberpunkColors.textSecondary,
      ),
      // Labels - Inter Medium
      labelLarge: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: CyberpunkColors.textPrimary,
      ),
      labelMedium: GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: CyberpunkColors.textSecondary,
      ),
      labelSmall: GoogleFonts.inter(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        letterSpacing: 1.5,
        color: CyberpunkColors.textMuted,
      ),
    );
  }

  // === AppBar Theme ===
  static AppBarTheme get _appBarTheme {
    return AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: GoogleFonts.orbitron(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: CyberpunkColors.textPrimary,
        letterSpacing: 1,
      ),
      iconTheme: const IconThemeData(color: CyberpunkColors.neonCyan),
    );
  }

  // === Card Theme ===
  static CardThemeData get _cardTheme {
    return CardThemeData(
      color: CyberpunkColors.surfaceCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5),
          width: 1,
        ),
      ),
      margin: const EdgeInsets.symmetric(vertical: 8),
    );
  }

  // === Elevated Button Theme ===
  static ElevatedButtonThemeData get _elevatedButtonTheme {
    return ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: CyberpunkColors.hotPink,
        foregroundColor: Colors.white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  // === Filled Button Theme ===
  static FilledButtonThemeData get _filledButtonTheme {
    return FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: CyberpunkColors.hotPink,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  // === Outlined Button Theme ===
  static OutlinedButtonThemeData get _outlinedButtonTheme {
    return OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: CyberpunkColors.neonCyan,
        side: const BorderSide(color: CyberpunkColors.neonCyan, width: 1.5),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  // === Text Button Theme ===
  static TextButtonThemeData get _textButtonTheme {
    return TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: CyberpunkColors.neonCyan,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        textStyle: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  // === Input Decoration Theme ===
  static InputDecorationTheme get _inputDecorationTheme {
    return InputDecorationTheme(
      filled: true,
      fillColor: CyberpunkColors.charcoal,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5),
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5),
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(
          color: CyberpunkColors.neonCyan,
          width: 2,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(
          color: CyberpunkColors.neonPinkGlow,
          width: 1,
        ),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(
          color: CyberpunkColors.neonPinkGlow,
          width: 2,
        ),
      ),
      labelStyle: GoogleFonts.inter(
        color: CyberpunkColors.textSecondary,
        fontSize: 14,
      ),
      hintStyle: GoogleFonts.inter(
        color: CyberpunkColors.textMuted,
        fontSize: 14,
      ),
      prefixIconColor: CyberpunkColors.neonCyan,
      suffixIconColor: CyberpunkColors.textSecondary,
    );
  }

  // === SnackBar Theme ===
  static SnackBarThemeData get _snackBarTheme {
    return SnackBarThemeData(
      backgroundColor: CyberpunkColors.charcoal,
      contentTextStyle: GoogleFonts.inter(
        color: CyberpunkColors.textPrimary,
        fontSize: 14,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5),
        ),
      ),
      behavior: SnackBarBehavior.floating,
    );
  }

  // === Progress Indicator Theme ===
  static ProgressIndicatorThemeData get _progressIndicatorTheme {
    return const ProgressIndicatorThemeData(
      color: CyberpunkColors.hotPink,
      linearTrackColor: CyberpunkColors.charcoal,
      circularTrackColor: CyberpunkColors.charcoal,
    );
  }

  // === Divider Theme ===
  static DividerThemeData get _dividerTheme {
    return DividerThemeData(
      color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5),
      thickness: 1,
      space: 24,
    );
  }

  // === Icon Theme ===
  static const IconThemeData _iconTheme = IconThemeData(
    color: CyberpunkColors.textSecondary,
    size: 24,
  );

  // === Dropdown Menu Theme ===
  static DropdownMenuThemeData get _dropdownMenuTheme {
    return DropdownMenuThemeData(
      menuStyle: MenuStyle(
        backgroundColor: WidgetStateProperty.all(CyberpunkColors.charcoal),
        shape: WidgetStateProperty.all(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: CyberpunkColors.surfaceBorder.withValues(alpha: 0.5),
            ),
          ),
        ),
      ),
    );
  }
}
