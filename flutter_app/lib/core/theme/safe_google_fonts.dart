import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// A utility class to generate Google Fonts that are safe for use on macOS/Desktop.
///
/// This class automatically applies `inherit: false` and `textBaseline: TextBaseline.alphabetic`
/// to prevent crashes related to font interpolation and null assertions in Flutter's
/// text rendering engine on specific platforms.
class SafeGoogleFonts {
  const SafeGoogleFonts._();

  /// Creates an Orbitron text style (Futuristic)
  static TextStyle orbitron(
    double size, {
    FontWeight weight = FontWeight.normal,
    Color? color,
    double? letterSpacing,
  }) {
    return GoogleFonts.orbitron(
      fontSize: size,
      fontWeight: weight,
      color: color,
      letterSpacing: letterSpacing,
      textBaseline: TextBaseline.alphabetic,
    ).copyWith(inherit: false);
  }

  /// Creates a Rajdhani text style (Technical/Square)
  static TextStyle rajdhani(
    double size, {
    FontWeight weight = FontWeight.normal,
    Color? color,
    double? letterSpacing,
  }) {
    return GoogleFonts.rajdhani(
      fontSize: size,
      fontWeight: weight,
      color: color,
      letterSpacing: letterSpacing,
      textBaseline: TextBaseline.alphabetic,
    ).copyWith(inherit: false);
  }

  /// Creates an Inter text style (Clean/Readable)
  static TextStyle inter(double fontSize,
      {FontWeight weight = FontWeight.normal,
      Color? color,
      double? letterSpacing}) {
    return GoogleFonts.inter(
      fontSize: fontSize,
      fontWeight: weight,
      color: color,
      letterSpacing: letterSpacing,
      textBaseline: TextBaseline.alphabetic,
    ).copyWith(inherit: false);
  }

  /// Space Grotesk - Quirky, modern sans-serif for NeoPop
  static TextStyle spaceGrotesk(double fontSize,
      {FontWeight weight = FontWeight.normal,
      Color? color,
      double? letterSpacing}) {
    return GoogleFonts.spaceGrotesk(
      fontSize: fontSize,
      fontWeight: weight,
      color: color,
      letterSpacing: letterSpacing,
      textBaseline: TextBaseline.alphabetic,
    ).copyWith(inherit: false);
  }

  /// Generic method for any Google Font if needed in the future
  static TextStyle get(
    String fontName,
    double size, {
    FontWeight weight = FontWeight.normal,
    Color? color,
    double? letterSpacing,
  }) {
    return GoogleFonts.getFont(
      fontName,
      fontSize: size,
      fontWeight: weight,
      color: color,
      letterSpacing: letterSpacing,
      textBaseline: TextBaseline.alphabetic,
    ).copyWith(inherit: false);
  }
}
