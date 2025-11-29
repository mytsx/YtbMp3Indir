import 'package:flutter/material.dart';

/// Cyberpunk Design System - Color Palette
/// Inspired by: Blade Runner, Cyberpunk 2077, Tron Legacy
class CyberpunkColors {
  CyberpunkColors._();

  // === Primary - Neon Accent Colors ===
  static const Color electricPurple = Color(0xFF711C91);
  static const Color hotPink = Color(0xFFEA00D9);
  static const Color neonCyan = Color(0xFF0ABDC6);
  static const Color electricBlue = Color(0xFF6300FF);

  // === Background - Dark Tones ===
  static const Color deepSpace = Color(0xFF0A0A0F);
  static const Color darkNavy = Color(0xFF091833);
  static const Color midnightPurple = Color(0xFF1A0A2E);
  static const Color charcoal = Color(0xFF1B1B2A);

  // === Accent - Glow Colors ===
  static const Color neonPinkGlow = Color(0xFFFF007A);
  static const Color cyberYellow = Color(0xFFF9C54E);
  static const Color matrixGreen = Color(0xFF00FFB3);
  static const Color iceBlue = Color(0xFF00BFFF);

  // === Semantic Colors ===
  static const Color success = matrixGreen;
  static const Color error = neonPinkGlow;
  static const Color warning = cyberYellow;
  static const Color info = iceBlue;

  // === Text Colors ===
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB0B0B0);
  static const Color textMuted = Color(0xFF6B6B6B);

  // === Surface Colors ===
  static const Color surfaceElevated = Color(0xFF1B1B2A);
  static const Color surfaceCard = Color(0xFF141420);
  static const Color surfaceBorder = Color(0xFF2A2A40);

  // === Gradients ===
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [electricPurple, hotPink, neonCyan],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient darkFadeGradient = LinearGradient(
    colors: [deepSpace, midnightPurple],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient neonButtonGradient = LinearGradient(
    colors: [hotPink, electricBlue],
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
  );

  static const LinearGradient cyanGradient = LinearGradient(
    colors: [neonCyan, electricBlue],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // === Glass Effect Colors ===
  static Color glassBackground = Colors.white.withValues(alpha: 0.05);
  static Color glassBorder = Colors.white.withValues(alpha: 0.1);
  static Color glassHighlight = Colors.white.withValues(alpha: 0.15);

  // === Shadows ===
  static List<BoxShadow> neonGlow(Color color, {double intensity = 0.5}) {
    return [
      BoxShadow(
        color: color.withValues(alpha: intensity),
        blurRadius: 20,
        spreadRadius: 0,
      ),
      BoxShadow(
        color: color.withValues(alpha: intensity * 0.5),
        blurRadius: 40,
        spreadRadius: 0,
      ),
    ];
  }

  static List<BoxShadow> get subtleGlow => [
        BoxShadow(
          color: hotPink.withValues(alpha: 0.1),
          blurRadius: 20,
          spreadRadius: -5,
        ),
      ];

  static List<BoxShadow> get cardShadow => [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.3),
          blurRadius: 20,
          offset: const Offset(0, 4),
        ),
      ];
}
