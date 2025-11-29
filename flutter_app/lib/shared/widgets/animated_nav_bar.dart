import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/cyberpunk_colors.dart';

/// Navigation item data
class NavItem {
  final IconData icon;
  final IconData selectedIcon;
  final String label;

  const NavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
  });
}

/// Modern animated bottom navigation bar with floating design
class AnimatedNavBar extends StatefulWidget {
  final int currentIndex;
  final Function(int) onTap;
  final List<NavItem> items;

  const AnimatedNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  });

  @override
  State<AnimatedNavBar> createState() => _AnimatedNavBarState();
}

class _AnimatedNavBarState extends State<AnimatedNavBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedNavBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.currentIndex != widget.currentIndex) {
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      decoration: BoxDecoration(
        // Glassmorphic background - adapt to theme
        gradient: LinearGradient(
          colors: isDarkMode
              ? [
                  Colors.white.withValues(alpha: 0.08),
                  Colors.white.withValues(alpha: 0.03),
                ]
              : [
                  Colors.white.withValues(alpha: 0.9),
                  Colors.white.withValues(alpha: 0.95),
                ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: isDarkMode
              ? Colors.white.withValues(alpha: 0.1)
              : CyberpunkColors.hotPink.withValues(alpha: 0.3),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: CyberpunkColors.hotPink
                .withValues(alpha: isDarkMode ? 0.1 : 0.15),
            blurRadius: 20,
            spreadRadius: -5,
          ),
          BoxShadow(
            color: Colors.black.withValues(alpha: isDarkMode ? 0.3 : 0.1),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: List.generate(widget.items.length, (index) {
                final item = widget.items[index];
                final isSelected = index == widget.currentIndex;

                return Expanded(
                  child: GestureDetector(
                    onTap: () => widget.onTap(index),
                    behavior: HitTestBehavior.translucent,
                    child: Container(
                      color: Colors.transparent,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          _NavBarItem(
                            item: item,
                            isSelected: isSelected,
                            animation: _controller,
                            isDarkMode: isDarkMode,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
      ),
    );
  }
}

class _NavBarItem extends StatelessWidget {
  final NavItem item;
  final bool isSelected;
  final Animation<double> animation;
  final bool isDarkMode;

  const _NavBarItem({
    required this.item,
    required this.isSelected,
    required this.animation,
    required this.isDarkMode,
  });

  @override
  Widget build(BuildContext context) {
    // Theme-aware colors
    final unselectedIconColor =
        isDarkMode ? CyberpunkColors.textSecondary : const Color(0xFF45454F);
    final labelColor =
        isDarkMode ? CyberpunkColors.textPrimary : const Color(0xFF1A1A2E);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeOutCubic,
      padding: EdgeInsets.symmetric(
        horizontal: isSelected ? 16 : 12,
        vertical: 8,
      ),
      decoration: BoxDecoration(
        // Neon glow background for selected item
        gradient: isSelected
            ? LinearGradient(
                colors: isDarkMode
                    ? [
                        CyberpunkColors.hotPink.withValues(alpha: 0.3),
                        CyberpunkColors.electricPurple.withValues(alpha: 0.2),
                      ]
                    : [
                        CyberpunkColors.hotPink.withValues(alpha: 0.15),
                        CyberpunkColors.electricPurple.withValues(alpha: 0.1),
                      ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : null,
        color: isSelected ? null : Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        border: isSelected
            ? Border.all(
                color: CyberpunkColors.hotPink
                    .withValues(alpha: isDarkMode ? 0.5 : 0.4),
                width: 1,
              )
            : null,
        boxShadow: isSelected
            ? [
                BoxShadow(
                  color: CyberpunkColors.hotPink
                      .withValues(alpha: isDarkMode ? 0.3 : 0.2),
                  blurRadius: 12,
                  spreadRadius: -2,
                ),
              ]
            : null,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          AnimatedScale(
            scale: isSelected ? 1.1 : 1.0,
            duration: const Duration(milliseconds: 200),
            child: ShaderMask(
              shaderCallback: isSelected
                  ? (bounds) => const LinearGradient(
                        colors: [
                          CyberpunkColors.hotPink,
                          CyberpunkColors.neonCyan,
                        ],
                      ).createShader(bounds)
                  : (bounds) => LinearGradient(
                        colors: [
                          unselectedIconColor,
                          unselectedIconColor,
                        ],
                      ).createShader(bounds),
              child: Icon(
                isSelected ? item.selectedIcon : item.icon,
                color: Colors.white,
                size: 24,
              ),
            ),
          ),
          AnimatedSize(
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOutCubic,
            child: isSelected
                ? Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: AnimatedOpacity(
                      opacity: isSelected ? 1.0 : 0.0,
                      duration: const Duration(milliseconds: 200),
                      child: Text(
                        item.label,
                        style: TextStyle(
                          color: labelColor,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  )
                : const SizedBox.shrink(),
          ),
        ],
      ),
    );
  }
}
