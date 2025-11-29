import 'package:flutter/material.dart';
import '../../core/theme/neo_pop_colors.dart';

class NeoPopBackground extends StatelessWidget {
  final Widget child;

  const NeoPopBackground({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor =
        isDark ? NeoPopColors.darkBackground : NeoPopColors.lightBackground;
    final dotColor = isDark
        ? NeoPopColors.starkWhite.withOpacity(0.1)
        : NeoPopColors.starkBlack.withOpacity(0.1);

    return Stack(
      children: [
        // Base background
        Container(color: bgColor),

        // Polka dot pattern
        CustomPaint(
          painter: PolkaDotPainter(color: dotColor),
          size: Size.infinite,
        ),

        // Random geometric shapes (static for now, could be animated)
        Positioned(
          top: -50,
          right: -50,
          child: _buildShape(
            width: 200,
            height: 200,
            color: NeoPopColors.vibrantYellow.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
        ),
        Positioned(
          bottom: 100,
          left: -20,
          child: _buildShape(
            width: 150,
            height: 150,
            color: NeoPopColors.hotPink.withOpacity(0.2),
            shape: BoxShape.rectangle,
            borderRadius: BorderRadius.circular(20),
          ),
        ),

        // Content
        child,
      ],
    );
  }

  Widget _buildShape({
    required double width,
    required double height,
    required Color color,
    required BoxShape shape,
    BorderRadius? borderRadius,
  }) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: color,
        shape: shape,
        borderRadius: borderRadius,
      ),
    );
  }
}

class PolkaDotPainter extends CustomPainter {
  final Color color;

  PolkaDotPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    const double spacing = 20.0;
    const double radius = 2.0;

    for (double x = 0; x < size.width; x += spacing) {
      for (double y = 0; y < size.height; y += spacing) {
        // Offset every other row for a honeycomb-ish look
        double xOffset = (y / spacing).floor() % 2 == 0 ? 0 : spacing / 2;
        canvas.drawCircle(Offset(x + xOffset, y), radius, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
