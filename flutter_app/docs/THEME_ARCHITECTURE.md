# Theme Architecture

This project uses a centralized and builder-based approach for theming to ensure consistency, stability, and ease of extension.

## Core Components

### 1. `SafeGoogleFonts` (`lib/core/theme/safe_google_fonts.dart`)
**Purpose:** Prevents crashes related to font inheritance and baseline alignment.
**Usage:** Always use `SafeGoogleFonts.fontName(...)` instead of `GoogleFonts.fontName(...)`.
**Why:** `GoogleFonts` by default can inherit properties that conflict with Flutter's text rendering engine in certain contexts (like `RichText` or specific widget trees), leading to "baseline not specified" errors. `SafeGoogleFonts` enforces `inherit: false` and `textBaseline: TextBaseline.alphabetic`.

### 2. `AppThemeBuilder` (`lib/core/theme/app_theme_builder.dart`)
**Purpose:** Eliminates code duplication between Light and Dark themes.
**Usage:**
```dart
final myTheme = AppThemeBuilder.build(
  colorScheme: myColorScheme,
  textTheme: myTextTheme,
  scaffoldBackgroundColor: myBackgroundColor,
);
```
**Why:** Instead of manually defining `AppBarTheme`, `InputDecorationTheme`, `CardTheme`, etc., for every single theme, `AppThemeBuilder` generates them automatically based on the provided `ColorScheme`. This ensures that all themes have a consistent "shape" and behavior, differing only in colors.

### 3. `CyberpunkTheme` (`lib/core/theme/cyberpunk_theme.dart`)
**Purpose:** The concrete implementation of the application's theme.
**Usage:** Access via `CyberpunkTheme.darkTheme` or `CyberpunkTheme.lightTheme`.
**Structure:** Defines the specific `ColorScheme` and `TextTheme` for the Cyberpunk look, then delegates the heavy lifting to `AppThemeBuilder`.

## How to Add a New Theme

1.  **Define Colors:** Create a new `ColorScheme`.
2.  **Define Typography:** Create a `TextTheme` using `SafeGoogleFonts`.
3.  **Build:** Call `AppThemeBuilder.build(...)`.

Example:
```dart
static ThemeData get matrixTheme {
  return AppThemeBuilder.build(
    colorScheme: _matrixColorScheme,
    textTheme: _matrixTextTheme,
    // ...
  );
}
```
