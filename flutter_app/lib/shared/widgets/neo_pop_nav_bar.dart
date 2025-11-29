import 'package:flutter/material.dart';
import '../../core/theme/neo_pop_colors.dart';
import 'animated_nav_bar.dart';

class NeoPopNavBar extends StatelessWidget {
  final int currentIndex;
  final List<NavItem> items;
  final Function(int) onTap;

  const NeoPopNavBar({
    super.key,
    required this.currentIndex,
    required this.items,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final borderColor =
        isDark ? NeoPopColors.starkWhite : NeoPopColors.starkBlack;
    final activeColor =
        isDark ? NeoPopColors.vibrantYellow : NeoPopColors.hotPink;
    final inactiveColor =
        isDark ? NeoPopColors.starkWhite : NeoPopColors.starkBlack;

    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? NeoPopColors.starkBlack : NeoPopColors.starkWhite,
        border: Border.all(color: borderColor, width: 3),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: borderColor,
            offset: const Offset(4, 4),
            blurRadius: 0, // Hard shadow
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: List.generate(items.length, (index) {
            final isSelected = currentIndex == index;
            final item = items[index];

            return GestureDetector(
              onTap: () => onTap(index),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected ? activeColor : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                  border: isSelected
                      ? Border.all(color: borderColor, width: 2)
                      : Border.all(color: Colors.transparent, width: 2),
                ),
                child: Row(
                  children: [
                    Icon(
                      isSelected ? item.selectedIcon : item.icon,
                      color: isSelected
                          ? (isDark
                              ? NeoPopColors.starkBlack
                              : NeoPopColors.starkWhite)
                          : inactiveColor,
                    ),
                    if (isSelected) ...[
                      const SizedBox(width: 8),
                      Text(
                        item.label,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: isDark
                              ? NeoPopColors.starkBlack
                              : NeoPopColors.starkWhite,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          }),
        ),
      ),
    );
  }
}

// Reusing the NavItem class definition if it's not public, otherwise import it.
// Assuming NavItem is defined in main.dart or similar, but since I can't import main.dart easily for a class inside it without circular deps if main imports this...
// I'll redefine a simple DTO here or expect it to be passed.
// Actually, looking at main.dart, NavItem seems to be a private class or defined inside _MainNavigationState?
// Wait, main.dart uses `NavItem` in `_navItems`. Let's check where `NavItem` is defined.
// It's likely in `animated_nav_bar.dart`.
