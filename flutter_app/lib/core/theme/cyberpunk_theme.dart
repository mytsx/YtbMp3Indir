import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'cyberpunk_colors.dart';
import 'app_theme_builder.dart';
import 'safe_google_fonts.dart';

/// Cyberpunk Design System - Theme Configuration
class CyberpunkTheme {
  CyberpunkTheme._();

  /// Dark theme (primary - this design is dark-mode only)
  static ThemeData get darkTheme {
    return AppThemeBuilder.build(
      colorScheme: _colorScheme,
      textTheme: _buildTextTheme(
        ThemeData.dark().textTheme,
        CyberpunkColors.textPrimary,
        CyberpunkColors.textSecondary,
      ),
      scaffoldBackgroundColor: CyberpunkColors.deepSpace,
    );
  }

  /// Light theme - Cyberpunk with light backgrounds
  static ThemeData get lightTheme {
    return AppThemeBuilder.build(
      colorScheme: _lightColorScheme,
      textTheme: _buildTextTheme(
        ThemeData.light().textTheme,
        const Color(0xFF1A1A2E),
        const Color(0xFF45454F),
      ),
      scaffoldBackgroundColor: const Color(0xFFF5F5FA),
    );
  }

  // === Color Scheme ===
  static const ColorScheme _lightColorScheme = ColorScheme(
    brightness: Brightness.light,
    primary: CyberpunkColors.hotPink,
    onPrimary: Colors.white,
    primaryContainer: Color(0xFFFFD9F2),
    onPrimaryContainer: CyberpunkColors.electricPurple,
    secondary: CyberpunkColors.neonCyan,
    onSecondary: Colors.white,
    secondaryContainer: Color(0xFFD0F5F8),
    onSecondaryContainer: Color(0xFF003D42),
    tertiary: CyberpunkColors.electricBlue,
    onTertiary: Colors.white,
    tertiaryContainer: Color(0xFFD6E3FF),
    onTertiaryContainer: Color(0xFF001B3D),
    error: CyberpunkColors.neonPinkGlow,
    onError: Colors.white,
    errorContainer: Color(0xFFFFDAD6),
    onErrorContainer: Color(0xFF410002),
    surface: Color(0xFFF5F5FA),
    onSurface: Color(0xFF1A1A2E),
    surfaceContainerHighest: Color(0xFFE8E8F0),
    onSurfaceVariant: Color(0xFF45454F),
    outline: Color(0xFF757580),
    outlineVariant: Color(0xFFC6C6D0),
    shadow: Colors.black,
    scrim: Colors.black,
    inverseSurface: Color(0xFF2F2F3D),
    onInverseSurface: Color(0xFFF2F2F8),
    inversePrimary: CyberpunkColors.hotPink,
  );

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

  // === Text Theme Builder ===
  static TextTheme _buildTextTheme(
      TextTheme base, Color primaryColor, Color secondaryColor) {
    // Use Inter as the base font
    final baseTextTheme = GoogleFonts.interTextTheme(base);

    return baseTextTheme.copyWith(
      // Display - Orbitron (futuristic)
      displayLarge: SafeGoogleFonts.orbitron(48,
          weight: FontWeight.bold, color: primaryColor, letterSpacing: 2),
      displayMedium: SafeGoogleFonts.orbitron(36,
          weight: FontWeight.bold, color: primaryColor, letterSpacing: 1.5),
      displaySmall: SafeGoogleFonts.orbitron(28,
          weight: FontWeight.w600, color: primaryColor, letterSpacing: 1),
      // Headlines - Rajdhani
      headlineLarge: SafeGoogleFonts.rajdhani(28,
          weight: FontWeight.w600, color: primaryColor),
      headlineMedium: SafeGoogleFonts.rajdhani(24,
          weight: FontWeight.w600, color: primaryColor),
      headlineSmall: SafeGoogleFonts.rajdhani(20,
          weight: FontWeight.w600, color: primaryColor),
      // Titles - Inter
      titleLarge: SafeGoogleFonts.inter(20,
          weight: FontWeight.w600, color: primaryColor),
      titleMedium: SafeGoogleFonts.inter(16,
          weight: FontWeight.w600, color: primaryColor),
      titleSmall: SafeGoogleFonts.inter(14,
          weight: FontWeight.w600, color: primaryColor),
      // Body - Inter
      bodyLarge: SafeGoogleFonts.inter(16,
          weight: FontWeight.normal, color: primaryColor),
      bodyMedium: SafeGoogleFonts.inter(14,
          weight: FontWeight.normal, color: primaryColor),
      bodySmall: SafeGoogleFonts.inter(12,
          weight: FontWeight.normal, color: secondaryColor),
      // Labels - Inter
      labelLarge: SafeGoogleFonts.inter(14,
          weight: FontWeight.w500, color: primaryColor),
      labelMedium: SafeGoogleFonts.inter(12,
          weight: FontWeight.w500, color: secondaryColor),
      labelSmall: SafeGoogleFonts.inter(10,
          weight: FontWeight.w500, color: secondaryColor, letterSpacing: 1.5),
    );
  }
}
