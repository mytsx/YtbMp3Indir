import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'cyberpunk_colors.dart';

/// Cyberpunk Design System - Theme Configuration
class CyberpunkTheme {
  CyberpunkTheme._();

  /// Dark theme (primary - this design is dark-mode only)
  static ThemeData get darkTheme {
    final base = ThemeData.dark(useMaterial3: true);

    return base.copyWith(
      scaffoldBackgroundColor: CyberpunkColors.deepSpace,
      colorScheme: _colorScheme,
      textTheme: _buildTextTheme(base.textTheme, CyberpunkColors.textPrimary,
          CyberpunkColors.textSecondary),
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
      radioTheme: _radioTheme,
      listTileTheme: _listTileTheme,
    );
  }

  /// Light theme - Cyberpunk with light backgrounds
  static ThemeData get lightTheme {
    final base = ThemeData.light(useMaterial3: true);

    return base.copyWith(
      scaffoldBackgroundColor: const Color(0xFFF5F5FA),
      colorScheme: _lightColorScheme,
      textTheme: _buildTextTheme(
          base.textTheme, const Color(0xFF1A1A2E), const Color(0xFF45454F)),
      appBarTheme: _lightAppBarTheme,
      cardTheme: _lightCardTheme,
      elevatedButtonTheme: _elevatedButtonTheme,
      filledButtonTheme: _filledButtonTheme,
      outlinedButtonTheme: _outlinedButtonTheme,
      textButtonTheme: _textButtonTheme,
      inputDecorationTheme: _lightInputDecorationTheme,
      snackBarTheme: _snackBarTheme,
      progressIndicatorTheme: _progressIndicatorTheme,
      dividerTheme: _lightDividerTheme,
      iconTheme: _lightIconTheme,
      dropdownMenuTheme: _lightDropdownMenuTheme,
      radioTheme: _lightRadioTheme,
      listTileTheme: _lightListTileTheme,
    );
  }

  // === Light Color Scheme ===
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
      displayLarge: GoogleFonts.orbitron(
        fontSize: 48,
        fontWeight: FontWeight.bold,
        letterSpacing: 2,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      displayMedium: GoogleFonts.orbitron(
        fontSize: 36,
        fontWeight: FontWeight.bold,
        letterSpacing: 1.5,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      displaySmall: GoogleFonts.orbitron(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        letterSpacing: 1,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      // Headlines - Rajdhani
      headlineLarge: GoogleFonts.rajdhani(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      headlineMedium: GoogleFonts.rajdhani(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      headlineSmall: GoogleFonts.rajdhani(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      // Titles - Inter
      titleLarge: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      titleMedium: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      titleSmall: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      // Body - Inter
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      bodySmall: GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.normal,
        color: secondaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      // Labels - Inter
      labelLarge: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: primaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      labelMedium: GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: secondaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      labelSmall: GoogleFonts.inter(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        letterSpacing: 1.5,
        color: secondaryColor,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
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
      ).copyWith(inherit: false),
      iconTheme: const IconThemeData(color: CyberpunkColors.neonCyan),
    );
  }

  // === Light AppBar Theme ===
  static AppBarTheme get _lightAppBarTheme {
    return AppBarTheme(
      backgroundColor: const Color(0xFFF5F5FA),
      elevation: 0,
      centerTitle: true,
      titleTextStyle: GoogleFonts.orbitron(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: const Color(0xFF1A1A2E),
        letterSpacing: 1,
      ).copyWith(inherit: false),
      iconTheme: const IconThemeData(color: CyberpunkColors.hotPink),
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
          color: CyberpunkColors.surfaceBorder.withOpacity(0.5),
          width: 1,
        ),
      ),
      margin: const EdgeInsets.symmetric(vertical: 8),
    );
  }

  // === Light Card Theme ===
  static CardThemeData get _lightCardTheme {
    return CardThemeData(
      color: Colors.white,
      elevation: 2,
      shadowColor: CyberpunkColors.hotPink.withOpacity(0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: CyberpunkColors.hotPink.withOpacity(0.2),
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
          textBaseline: TextBaseline.alphabetic,
        ).copyWith(inherit: false),
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
          textBaseline: TextBaseline.alphabetic,
        ).copyWith(inherit: false),
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
          textBaseline: TextBaseline.alphabetic,
        ).copyWith(inherit: false),
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
          textBaseline: TextBaseline.alphabetic,
        ).copyWith(inherit: false),
      ),
    );
  }

  // === Input Decoration Theme ===
  static InputDecorationTheme get _inputDecorationTheme {
    return InputDecorationTheme(
      filled: true,
      fillColor: CyberpunkColors.charcoal,
      isDense: false,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: CyberpunkColors.surfaceBorder.withOpacity(0.5),
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: CyberpunkColors.surfaceBorder.withOpacity(0.5),
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
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      floatingLabelStyle: GoogleFonts.inter(
        color: CyberpunkColors.neonCyan,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      hintStyle: GoogleFonts.inter(
        color: CyberpunkColors.textMuted,
        fontSize: 14,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      errorStyle: GoogleFonts.inter(
        color: CyberpunkColors.neonPinkGlow,
        fontSize: 12,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      helperStyle: GoogleFonts.inter(
        color: CyberpunkColors.textMuted,
        fontSize: 12,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      prefixIconColor: CyberpunkColors.neonCyan,
      suffixIconColor: CyberpunkColors.textSecondary,
    );
  }

  // === Light Input Decoration Theme ===
  static InputDecorationTheme get _lightInputDecorationTheme {
    return InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      isDense: false,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: CyberpunkColors.hotPink.withOpacity(0.3),
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: CyberpunkColors.hotPink.withOpacity(0.3),
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(
          color: CyberpunkColors.hotPink,
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
        color: const Color(0xFF45454F),
        fontSize: 14,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      floatingLabelStyle: GoogleFonts.inter(
        color: CyberpunkColors.hotPink,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      hintStyle: GoogleFonts.inter(
        color: const Color(0xFF757580),
        fontSize: 14,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      errorStyle: GoogleFonts.inter(
        color: CyberpunkColors.neonPinkGlow,
        fontSize: 12,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      helperStyle: GoogleFonts.inter(
        color: const Color(0xFF757580),
        fontSize: 12,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      prefixIconColor: CyberpunkColors.hotPink,
      suffixIconColor: const Color(0xFF45454F),
    );
  }

  // === SnackBar Theme ===
  static SnackBarThemeData get _snackBarTheme {
    return SnackBarThemeData(
      backgroundColor: CyberpunkColors.charcoal,
      contentTextStyle: GoogleFonts.inter(
        color: CyberpunkColors.textPrimary,
        fontSize: 14,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: CyberpunkColors.surfaceBorder.withOpacity(0.5),
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
      color: CyberpunkColors.surfaceBorder.withOpacity(0.5),
      thickness: 1,
      space: 24,
    );
  }

  // === Light Divider Theme ===
  static DividerThemeData get _lightDividerTheme {
    return DividerThemeData(
      color: CyberpunkColors.hotPink.withOpacity(0.2),
      thickness: 1,
      space: 24,
    );
  }

  // === Icon Theme ===
  static const IconThemeData _iconTheme = IconThemeData(
    color: CyberpunkColors.textSecondary,
    size: 24,
  );

  // === Light Icon Theme ===
  static const IconThemeData _lightIconTheme = IconThemeData(
    color: Color(0xFF45454F),
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
              color: CyberpunkColors.surfaceBorder.withOpacity(0.5),
            ),
          ),
        ),
      ),
    );
  }

  // === Light Dropdown Menu Theme ===
  static DropdownMenuThemeData get _lightDropdownMenuTheme {
    return DropdownMenuThemeData(
      menuStyle: MenuStyle(
        backgroundColor: WidgetStateProperty.all(Colors.white),
        shape: WidgetStateProperty.all(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: CyberpunkColors.hotPink.withOpacity(0.2),
            ),
          ),
        ),
      ),
    );
  }

  // === Radio Theme (Dark) ===
  static RadioThemeData get _radioTheme {
    return RadioThemeData(
      fillColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return CyberpunkColors.hotPink;
        }
        return CyberpunkColors.textSecondary;
      }),
      overlayColor: WidgetStateProperty.all(
        CyberpunkColors.hotPink.withOpacity(0.1),
      ),
    );
  }

  // === Radio Theme (Light) ===
  static RadioThemeData get _lightRadioTheme {
    return RadioThemeData(
      fillColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return CyberpunkColors.hotPink;
        }
        return const Color(0xFF45454F);
      }),
      overlayColor: WidgetStateProperty.all(
        CyberpunkColors.hotPink.withOpacity(0.1),
      ),
    );
  }

  // === ListTile Theme (Dark) ===
  static ListTileThemeData get _listTileTheme {
    return ListTileThemeData(
      iconColor: CyberpunkColors.textSecondary,
      textColor: CyberpunkColors.textPrimary,
      titleTextStyle: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: CyberpunkColors.textPrimary,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      subtitleTextStyle: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: CyberpunkColors.textSecondary,
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
    );
  }

  // === ListTile Theme (Light) ===
  static ListTileThemeData get _lightListTileTheme {
    return ListTileThemeData(
      iconColor: const Color(0xFF45454F),
      textColor: const Color(0xFF1A1A2E),
      titleTextStyle: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: const Color(0xFF1A1A2E),
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      subtitleTextStyle: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: const Color(0xFF45454F),
        textBaseline: TextBaseline.alphabetic,
      ).copyWith(inherit: false),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
    );
  }
}
