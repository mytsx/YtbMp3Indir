import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'neo_pop_colors.dart';
import 'app_theme_builder.dart';
import 'safe_google_fonts.dart';

/// NeoPop Design System - Bold, Brutalist, Fun
class NeoPopTheme {
  NeoPopTheme._();

  /// Dark theme
  static ThemeData get darkTheme {
    return AppThemeBuilder.build(
      colorScheme: _darkColorScheme,
      textTheme: _buildTextTheme(
        ThemeData.dark().textTheme,
        NeoPopColors.starkWhite,
        NeoPopColors.vibrantYellow,
      ),
      scaffoldBackgroundColor: NeoPopColors.darkBackground,
    ).copyWith(
      // Override specific components for the "Brutalist" look
      cardTheme: CardThemeData(
        color: NeoPopColors.starkBlack,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
          side: const BorderSide(color: NeoPopColors.starkWhite, width: 2),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: NeoPopColors.vibrantYellow,
          foregroundColor: NeoPopColors.starkBlack,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4),
            side: const BorderSide(color: NeoPopColors.starkWhite, width: 2),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        ),
      ),
    );
  }

  /// Light theme
  static ThemeData get lightTheme {
    return AppThemeBuilder.build(
      colorScheme: _lightColorScheme,
      textTheme: _buildTextTheme(
        ThemeData.light().textTheme,
        NeoPopColors.starkBlack,
        NeoPopColors.deepPurple,
      ),
      scaffoldBackgroundColor: NeoPopColors.lightBackground,
    ).copyWith(
      // Override specific components for the "Brutalist" look
      cardTheme: CardThemeData(
        color: NeoPopColors.starkWhite,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
          side: const BorderSide(color: NeoPopColors.starkBlack, width: 3),
        ),
        shadowColor: NeoPopColors.starkBlack,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: NeoPopColors.hotPink,
          foregroundColor: NeoPopColors.starkWhite,
          elevation:
              8, // Hard shadow simulated via elevation? No, Flutter blurs it.
          // We might need custom widgets for true hard shadows, but we'll do our best here.
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4),
            side: const BorderSide(color: NeoPopColors.starkBlack, width: 3),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        ),
      ),
    );
  }

  // === Color Scheme (Light) ===
  static const ColorScheme _lightColorScheme = ColorScheme(
    brightness: Brightness.light,
    primary: NeoPopColors.starkBlack,
    onPrimary: NeoPopColors.starkWhite,
    primaryContainer: NeoPopColors.vibrantYellow,
    onPrimaryContainer: NeoPopColors.starkBlack,
    secondary: NeoPopColors.hotPink,
    onSecondary: NeoPopColors.starkWhite,
    secondaryContainer: NeoPopColors.electricBlue,
    onSecondaryContainer: NeoPopColors.starkWhite,
    tertiary: NeoPopColors.limeGreen,
    onTertiary: NeoPopColors.starkBlack,
    error: NeoPopColors.error,
    onError: NeoPopColors.starkWhite,
    surface: NeoPopColors.starkWhite,
    onSurface: NeoPopColors.starkBlack,
    outline: NeoPopColors.starkBlack,
  );

  // === Color Scheme (Dark) ===
  static const ColorScheme _darkColorScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: NeoPopColors.starkWhite,
    onPrimary: NeoPopColors.starkBlack,
    primaryContainer: NeoPopColors.electricBlue,
    onPrimaryContainer: NeoPopColors.starkWhite,
    secondary: NeoPopColors.vibrantYellow,
    onSecondary: NeoPopColors.starkBlack,
    secondaryContainer: NeoPopColors.hotPink,
    onSecondaryContainer: NeoPopColors.starkWhite,
    tertiary: NeoPopColors.limeGreen,
    onTertiary: NeoPopColors.starkBlack,
    error: NeoPopColors.error,
    onError: NeoPopColors.starkWhite,
    surface: NeoPopColors.starkBlack,
    onSurface: NeoPopColors.starkWhite,
    outline: NeoPopColors.starkWhite,
  );

  // === Text Theme Builder ===
  static TextTheme _buildTextTheme(
      TextTheme base, Color primaryColor, Color secondaryColor) {
    // Use Space Grotesk as the base font
    final baseTextTheme = GoogleFonts.spaceGroteskTextTheme(base);

    return baseTextTheme.copyWith(
      displayLarge: SafeGoogleFonts.spaceGrotesk(48,
          weight: FontWeight.w900, color: primaryColor, letterSpacing: -1),
      displayMedium: SafeGoogleFonts.spaceGrotesk(36,
          weight: FontWeight.bold, color: primaryColor, letterSpacing: -0.5),
      displaySmall: SafeGoogleFonts.spaceGrotesk(28,
          weight: FontWeight.bold, color: primaryColor),
      headlineLarge: SafeGoogleFonts.spaceGrotesk(28,
          weight: FontWeight.bold, color: primaryColor),
      headlineMedium: SafeGoogleFonts.spaceGrotesk(24,
          weight: FontWeight.bold, color: primaryColor),
      headlineSmall: SafeGoogleFonts.spaceGrotesk(20,
          weight: FontWeight.bold, color: primaryColor),
      titleLarge: SafeGoogleFonts.spaceGrotesk(20,
          weight: FontWeight.bold, color: primaryColor),
      titleMedium: SafeGoogleFonts.spaceGrotesk(16,
          weight: FontWeight.bold, color: primaryColor),
      titleSmall: SafeGoogleFonts.spaceGrotesk(14,
          weight: FontWeight.bold, color: primaryColor),
      bodyLarge: SafeGoogleFonts.spaceGrotesk(16,
          weight: FontWeight.normal, color: primaryColor),
      bodyMedium: SafeGoogleFonts.spaceGrotesk(14,
          weight: FontWeight.normal, color: primaryColor),
      bodySmall: SafeGoogleFonts.spaceGrotesk(12,
          weight: FontWeight.normal, color: secondaryColor),
      labelLarge: SafeGoogleFonts.spaceGrotesk(14,
          weight: FontWeight.w700, color: primaryColor),
      labelMedium: SafeGoogleFonts.spaceGrotesk(12,
          weight: FontWeight.w700, color: secondaryColor),
      labelSmall: SafeGoogleFonts.spaceGrotesk(10,
          weight: FontWeight.w700, color: secondaryColor),
    );
  }
}
