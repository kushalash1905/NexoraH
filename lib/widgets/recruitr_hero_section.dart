import 'dart:io' show Platform;
import 'dart:math' as math;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

/// Dramatic, minimal, premium RecruitR landing / hero section.
/// Positioned above the existing UI with an artistic editorial introduction,
/// huge typography, slow animated architectural logo, and generous whitespace.
/// Free of unnecessary AI/filler micro-text.
class RecruitRHeroSection extends StatefulWidget {
  final VoidCallback? onExploreTap;
  final double scrollProgress; // 0.0 (fully visible) to 1.0 (scrolled past)

  const RecruitRHeroSection({
    super.key,
    this.onExploreTap,
    this.scrollProgress = 0.0,
  });

  @override
  State<RecruitRHeroSection> createState() => _RecruitRHeroSectionState();
}

class _RecruitRHeroSectionState extends State<RecruitRHeroSection>
    with TickerProviderStateMixin {
  late AnimationController _ambientController;
  late AnimationController _entranceController;
  late Animation<double> _entranceFade;
  late Animation<double> _entranceScale;
  late Animation<Offset> _entranceSlide;

  bool get _isTestEnvironment {
    try {
      return !kIsWeb && Platform.environment.containsKey('FLUTTER_TEST');
    } catch (_) {
      return false;
    }
  }

  @override
  void initState() {
    super.initState();

    // Slow, elegant, artistic continuous loop (12 seconds period)
    _ambientController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 12),
    );
    if (!_isTestEnvironment) {
      _ambientController.repeat();
    }

    // Entrance reveal animation on screen load
    _entranceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );

    _entranceFade = CurvedAnimation(
      parent: _entranceController,
      curve: const Interval(0.0, 0.85, curve: Curves.easeOutCubic),
    );

    _entranceScale = Tween<double>(begin: 0.94, end: 1.0).animate(
      CurvedAnimation(
        parent: _entranceController,
        curve: Curves.easeOutCubic,
      ),
    );

    _entranceSlide = Tween<Offset>(
      begin: const Offset(0, 0.05),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _entranceController,
        curve: Curves.easeOutCubic,
      ),
    );

    _entranceController.forward();
  }

  @override
  void dispose() {
    _ambientController.dispose();
    _entranceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    final isCompact = screenWidth < 960;
    final paddingH = isCompact ? 24.0 : 54.0;

    // Fade and translate hero as user scrolls down
    final scrollFade = (1.0 - (widget.scrollProgress * 1.5)).clamp(0.0, 1.0);
    final scrollParallax = -widget.scrollProgress * 120.0;

    return Opacity(
      opacity: scrollFade,
      child: Transform.translate(
        offset: Offset(0, scrollParallax),
        child: Container(
          width: double.infinity,
          height: screenHeight,
          color: AppColors.canvas,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // 1. Subtle Animated Architectural Reticle & Logo Element Behind Wordmark
              Positioned.fill(
                child: AnimatedBuilder(
                  animation: _ambientController,
                  builder: (context, child) {
                    return CustomPaint(
                      painter: _RecruitRLogoPainter(
                        animationValue: _ambientController.value,
                        isCompact: isCompact,
                      ),
                    );
                  },
                ),
              ),

              // 2. Centered Dramatic RecruitR Wordmark with Generous Whitespace
              SlideTransition(
                position: _entranceSlide,
                child: ScaleTransition(
                  scale: _entranceScale,
                  child: FadeTransition(
                    opacity: _entranceFade,
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: paddingH),
                      child: AnimatedBuilder(
                        animation: _ambientController,
                        builder: (context, child) {
                          final wave = math.sin(_ambientController.value * 2 * math.pi);
                          return Text.rich(
                            TextSpan(
                              children: [
                                TextSpan(
                                  text: 'Recruit',
                                  style: GoogleFonts.syne(
                                    fontSize: isCompact ? 60 : (screenWidth < 1300 ? 98 : 126),
                                    fontWeight: FontWeight.w800,
                                    letterSpacing: isCompact ? -2.2 : -4.5,
                                    color: AppColors.textWhite,
                                    height: 0.95,
                                  ),
                                ),
                                TextSpan(
                                  text: 'R',
                                  style: GoogleFonts.syne(
                                    fontSize: isCompact ? 60 : (screenWidth < 1300 ? 98 : 126),
                                    fontWeight: FontWeight.w800,
                                    letterSpacing: isCompact ? -2.2 : -4.5,
                                    color: AppColors.pastelPink,
                                    height: 0.95,
                                    shadows: [
                                      Shadow(
                                        color: AppColors.pastelPink.withValues(
                                          alpha: 0.28 + (0.16 * wave),
                                        ),
                                        blurRadius: 32,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            textAlign: TextAlign.center,
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),

              // 3. Minimalist Scroll Invitation at Bottom
              Positioned(
                bottom: 40,
                child: FadeTransition(
                  opacity: _entranceFade,
                  child: MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: widget.onExploreTap,
                      child: AnimatedBuilder(
                        animation: _ambientController,
                        builder: (context, child) {
                          final bounce = math.sin(_ambientController.value * 2 * math.pi) * 3.5;
                          return Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                '[ SCROLL TO EXPLORE ARCHIVE ]',
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 1.8,
                                  color: AppColors.textMuted,
                                ),
                              ),
                              const SizedBox(height: 10),
                              Transform.translate(
                                offset: Offset(0, bounce),
                                child: Container(
                                  padding: const EdgeInsets.all(6),
                                  decoration: BoxDecoration(
                                    border: Border.all(
                                      color: AppColors.hairlineActive,
                                      width: 0.8,
                                    ),
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.arrow_downward,
                                    size: 13,
                                    color: AppColors.pastelPink,
                                  ),
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Custom painter for the animated geometric RecruitR emblem and architectural reticle.
/// Adopts cozy sophisticated pastel pink accents.
class _RecruitRLogoPainter extends CustomPainter {
  final double animationValue; // 0.0 to 1.0
  final bool isCompact;

  _RecruitRLogoPainter({
    required this.animationValue,
    required this.isCompact,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final baseRadius = isCompact ? 140.0 : 230.0;

    // Slow sinusoidal breathing factor
    final breath = math.sin(animationValue * 2 * math.pi);
    final slowRotation = animationValue * 2 * math.pi;

    // 1. Soft Cozy Radial Glow behind center wordmark
    final glowRadius = baseRadius * (1.3 + (0.15 * breath));
    final glowPaint = Paint()
      ..shader = RadialGradient(
        colors: [
          AppColors.pastelPink.withValues(alpha: 0.07 + (0.04 * breath)),
          AppColors.pastelPink.withValues(alpha: 0.015),
          Colors.transparent,
        ],
        stops: const [0.0, 0.45, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: glowRadius));
    canvas.drawCircle(center, glowRadius, glowPaint);

    // 2. Concentric Architectural Rings
    final ringPaint1 = Paint()
      ..color = AppColors.hairlineSubtle
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8;

    final ringPaint2 = Paint()
      ..color = AppColors.hairline
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8;

    final accentPaint = Paint()
      ..color = AppColors.pastelPink.withValues(alpha: 0.25)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    // Inner subtle ring
    canvas.drawCircle(center, baseRadius * 0.72, ringPaint1);

    // Mid structural ring
    canvas.drawCircle(center, baseRadius, ringPaint2);

    // Outer subtle ring
    canvas.drawCircle(center, baseRadius * 1.35, ringPaint1);

    // 3. Rotating Cardinal Reticle Ticks (slow clockwise)
    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(slowRotation * 0.15); // very slow 1.25 min rotation

    final tickLength = isCompact ? 7.0 : 12.0;
    const numTicks = 24;
    for (int i = 0; i < numTicks; i++) {
      final angle = (i * 2 * math.pi) / numTicks;
      final isMajor = i % 6 == 0;
      final p1 = Offset(
        math.cos(angle) * (baseRadius - (isMajor ? tickLength : tickLength * 0.5)),
        math.sin(angle) * (baseRadius - (isMajor ? tickLength : tickLength * 0.5)),
      );
      final p2 = Offset(
        math.cos(angle) * baseRadius,
        math.sin(angle) * baseRadius,
      );
      canvas.drawLine(p1, p2, isMajor ? accentPaint : ringPaint1);
    }

    // 4. Subtle Architectural Geometric "R" Monogram vector behind text
    final glyphSize = baseRadius * 0.65;
    final rPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.035 + (0.015 * breath))
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    // Draw stylized architectural geometry: vertical spine, arc, and diagonal leg
    final spineX = -glyphSize * 0.38;
    final topY = -glyphSize * 0.5;
    final midY = 0.0;
    final botY = glyphSize * 0.5;

    // Vertical spine
    canvas.drawLine(Offset(spineX, topY), Offset(spineX, botY), rPaint);

    // Horizontal top bar
    canvas.drawLine(Offset(spineX, topY), Offset(0, topY), rPaint);

    // Semi-circle upper bowl
    final bowlRect = Rect.fromLTRB(-glyphSize * 0.1, topY, glyphSize * 0.38, midY);
    canvas.drawArc(bowlRect, -math.pi / 2, math.pi, false, rPaint);

    // Horizontal mid bar
    canvas.drawLine(Offset(spineX, midY), Offset(0, midY), rPaint);

    // Angled leg
    canvas.drawLine(Offset(0, midY), Offset(glyphSize * 0.38, botY), rPaint);

    canvas.restore();

    // 5. Counter-rotating Outer Orbital Arc
    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(-slowRotation * 0.2); // Counter rotation

    final orbitalRect = Rect.fromCircle(center: Offset.zero, radius: baseRadius * 1.35);
    final arcSweep = math.pi * 0.35;
    canvas.drawArc(orbitalRect, 0, arcSweep, false, accentPaint);
    canvas.drawArc(orbitalRect, math.pi, arcSweep, false, accentPaint);

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _RecruitRLogoPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue ||
        oldDelegate.isCompact != isCompact;
  }
}
