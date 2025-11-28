import 'dart:math';
import 'package:flutter/material.dart';

/// Animated splash screen with grid animation
class SplashScreen extends StatefulWidget {
  final String statusMessage;

  const SplashScreen({
    super.key,
    this.statusMessage = 'Loading...',
  });

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  static const int gridSize = 8;
  late List<List<Color>> boxColors;
  late List<List<double>> boxOpacities;
  late AnimationController _waveController;
  final Random _random = Random();

  int waveCenterX = 0;
  int waveCenterY = 0;

  @override
  void initState() {
    super.initState();

    // Initialize grid colors and opacities
    boxColors = List.generate(
      gridSize,
      (_) => List.generate(gridSize, (_) => Colors.black.withOpacity(0.3)),
    );
    boxOpacities = List.generate(
      gridSize,
      (_) => List.generate(gridSize, (_) => 0.0),
    );

    // Wave animation
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _waveController.addListener(_updateWave);
    _waveController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        // Reset wave from new random point
        waveCenterX = _random.nextInt(gridSize);
        waveCenterY = _random.nextInt(gridSize);
        _waveController.reset();
        _waveController.forward();
      }
    });

    // Start animations
    _startFadeIn();
  }

  void _startFadeIn() async {
    // Fade in boxes one by one
    final indices = <int>[];
    for (int i = 0; i < gridSize * gridSize; i++) {
      indices.add(i);
    }
    indices.shuffle(_random);

    for (int i = 0; i < indices.length; i++) {
      await Future.delayed(const Duration(milliseconds: 15));
      if (!mounted) return;

      final idx = indices[i];
      final row = idx ~/ gridSize;
      final col = idx % gridSize;

      setState(() {
        boxOpacities[row][col] = 1.0;
      });
    }

    // Start wave animation after fade in
    await Future.delayed(const Duration(milliseconds: 300));
    if (mounted) {
      waveCenterX = _random.nextInt(gridSize);
      waveCenterY = _random.nextInt(gridSize);
      _waveController.forward();
    }
  }

  void _updateWave() {
    if (!mounted) return;

    final waveRadius = _waveController.value * gridSize * 1.5;

    setState(() {
      for (int row = 0; row < gridSize; row++) {
        for (int col = 0; col < gridSize; col++) {
          final dx = col - waveCenterX;
          final dy = row - waveCenterY;
          final distance = sqrt(dx * dx + dy * dy);

          if ((distance - waveRadius).abs() < 1.5) {
            // In wave - random color
            boxColors[row][col] = Color.fromRGBO(
              50 + _random.nextInt(205),
              50 + _random.nextInt(205),
              50 + _random.nextInt(205),
              0.7,
            );
          } else {
            // Outside wave - dark
            boxColors[row][col] = Colors.black.withOpacity(0.3);
          }
        }
      }
    });
  }

  @override
  void dispose() {
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDark ? Colors.grey[900] : Colors.grey[100],
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Animated grid
            Container(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: List.generate(gridSize, (row) {
                  return Row(
                    mainAxisSize: MainAxisSize.min,
                    children: List.generate(gridSize, (col) {
                      return AnimatedOpacity(
                        opacity: boxOpacities[row][col],
                        duration: const Duration(milliseconds: 200),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 100),
                          margin: const EdgeInsets.all(2),
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: boxColors[row][col],
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      );
                    }),
                  );
                }),
              ),
            ),

            const SizedBox(height: 32),

            // App title
            Text(
              'MP3 Yap',
              style: theme.textTheme.headlineLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: isDark ? Colors.white : Colors.black87,
              ),
            ),

            const SizedBox(height: 24),

            // Status message
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              decoration: BoxDecoration(
                color: isDark
                    ? Colors.black.withOpacity(0.5)
                    : Colors.black.withOpacity(0.7),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white.withOpacity(0.8),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    widget.statusMessage,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
