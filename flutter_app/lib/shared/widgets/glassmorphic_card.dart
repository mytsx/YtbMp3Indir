import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/cyberpunk_colors.dart';

/// A glassmorphic card widget with blur effect and neon border
class GlassmorphicCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final Color? glowColor;
  final double glowIntensity;
  final bool enableBlur;
  final double blurAmount;
  final VoidCallback? onTap;

  const GlassmorphicCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.borderRadius = 16,
    this.glowColor,
    this.glowIntensity = 0.1,
    this.enableBlur = true,
    this.blurAmount = 10,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveGlowColor = glowColor ?? CyberpunkColors.hotPink;

    Widget content = Container(
      margin: margin,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.white.withValues(alpha: 0.08),
            Colors.white.withValues(alpha: 0.03),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.1),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: effectiveGlowColor.withValues(alpha: glowIntensity),
            blurRadius: 20,
            spreadRadius: -5,
          ),
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: enableBlur
            ? BackdropFilter(
                filter: ImageFilter.blur(
                  sigmaX: blurAmount,
                  sigmaY: blurAmount,
                ),
                child: Padding(
                  padding: padding ?? const EdgeInsets.all(20),
                  child: child,
                ),
              )
            : Padding(
                padding: padding ?? const EdgeInsets.all(20),
                child: child,
              ),
      ),
    );

    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        child: content,
      );
    }

    return content;
  }
}

/// A glassmorphic button with neon glow effect
class NeonButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Color? glowColor;
  final bool isLoading;
  final EdgeInsetsGeometry? padding;

  const NeonButton({
    super.key,
    required this.child,
    this.onPressed,
    this.glowColor,
    this.isLoading = false,
    this.padding,
  });

  @override
  State<NeonButton> createState() => _NeonButtonState();
}

class _NeonButtonState extends State<NeonButton>
    with SingleTickerProviderStateMixin {
  bool _isHovered = false;
  late AnimationController _controller;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );
    _glowAnimation = Tween<double>(begin: 0.3, end: 0.6).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final effectiveGlowColor = widget.glowColor ?? CyberpunkColors.hotPink;
    final isEnabled = widget.onPressed != null && !widget.isLoading;

    return MouseRegion(
      onEnter: (_) {
        if (isEnabled) {
          setState(() => _isHovered = true);
          _controller.forward();
        }
      },
      onExit: (_) {
        setState(() => _isHovered = false);
        _controller.reverse();
      },
      child: AnimatedBuilder(
        animation: _glowAnimation,
        builder: (context, child) {
          return AnimatedScale(
            scale: _isHovered ? 1.02 : 1.0,
            duration: const Duration(milliseconds: 200),
            child: Container(
              decoration: BoxDecoration(
                gradient: isEnabled
                    ? CyberpunkColors.neonButtonGradient
                    : const LinearGradient(
                        colors: [
                          CyberpunkColors.charcoal,
                          CyberpunkColors.charcoal,
                        ],
                      ),
                borderRadius: BorderRadius.circular(12),
                boxShadow: isEnabled
                    ? [
                        BoxShadow(
                          color: effectiveGlowColor
                              .withValues(alpha: _glowAnimation.value),
                          blurRadius: 20,
                          spreadRadius: 0,
                        ),
                        BoxShadow(
                          color: CyberpunkColors.electricBlue
                              .withValues(alpha: _glowAnimation.value * 0.5),
                          blurRadius: 40,
                          spreadRadius: 0,
                        ),
                      ]
                    : [],
              ),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: isEnabled ? widget.onPressed : null,
                  borderRadius: BorderRadius.circular(12),
                  child: Padding(
                    padding: widget.padding ??
                        const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                    child: widget.isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : DefaultTextStyle(
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                            child: IconTheme(
                              data: const IconThemeData(
                                color: Colors.white,
                                size: 20,
                              ),
                              child: widget.child,
                            ),
                          ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

/// A container with animated gradient background
class CyberpunkBackground extends StatefulWidget {
  final Widget child;
  final bool animate;

  const CyberpunkBackground({
    super.key,
    required this.child,
    this.animate = true,
  });

  @override
  State<CyberpunkBackground> createState() => _CyberpunkBackgroundState();
}

class _CyberpunkBackgroundState extends State<CyberpunkBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    );
    if (widget.animate) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.animate) {
      return Container(
        decoration: const BoxDecoration(
          gradient: CyberpunkColors.darkFadeGradient,
        ),
        child: widget.child,
      );
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                CyberpunkColors.deepSpace,
                CyberpunkColors.midnightPurple,
                CyberpunkColors.darkNavy,
                CyberpunkColors.electricPurple.withValues(alpha: 0.2),
              ],
              stops: [
                0.0,
                0.3 + (_controller.value * 0.2),
                0.6 + (_controller.value * 0.1),
                1.0,
              ],
            ),
          ),
          child: widget.child,
        );
      },
    );
  }
}
