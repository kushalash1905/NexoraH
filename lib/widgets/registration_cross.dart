import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Iconic 22px hairline registration crosshair mark (`+`)
/// matching Camille Mormal's `#h-cross` spatial geometry.
class RegistrationCross extends StatelessWidget {
  final double size;
  final Color? color;
  final double strokeWidth;

  const RegistrationCross({
    super.key,
    this.size = 20.0,
    this.color,
    this.strokeWidth = 1.0,
  });

  @override
  Widget build(BuildContext context) {
    final paintColor = color ?? AppColors.crosshair;

    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _CrossPainter(
          color: paintColor,
          strokeWidth: strokeWidth,
        ),
      ),
    );
  }
}

class _CrossPainter extends CustomPainter {
  final Color color;
  final double strokeWidth;

  _CrossPainter({
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.square;

    final midX = size.width / 2;
    final midY = size.height / 2;

    // Horizontal arm
    canvas.drawLine(Offset(0, midY), Offset(size.width, midY), paint);
    // Vertical arm
    canvas.drawLine(Offset(midX, 0), Offset(midX, size.height), paint);
  }

  @override
  bool shouldRepaint(covariant _CrossPainter oldDelegate) {
    return oldDelegate.color != color || oldDelegate.strokeWidth != strokeWidth;
  }
}
