import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import 'registration_cross.dart';
import 'spatial_resume_plate.dart';

typedef OnCandidateSelected = void Function(Candidate candidate);

class SpatialResumeCanvas extends StatelessWidget {
  final List<Candidate> candidates;
  final OnCandidateSelected onSelectCandidate;

  const SpatialResumeCanvas({
    super.key,
    required this.candidates,
    required this.onSelectCandidate,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1100;

    if (candidates.isEmpty) {
      return const SizedBox.shrink();
    }

    if (!isDesktop) {
      // Responsive vertical spatial flow for smaller viewports
      return _buildMobileResponsiveFlow(context, screenWidth);
    }

    // High-End Desktop Spatial Canvas
    return _buildDesktopSpatialFlow(context, screenWidth);
  }

  Widget _buildDesktopSpatialFlow(BuildContext context, double screenWidth) {
    final List<Widget> children = [];

    // Subtle Section Header inside the canvas
    children.add(
      Padding(
        padding: const EdgeInsets.only(left: 48, right: 48, top: 40, bottom: 60),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const RegistrationCross(size: 22),
            Text(
              '// SPATIAL DOSSIER REPOSITORY · 18 CANDIDATES INDEXED',
              style: GoogleFonts.jetBrainsMono(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.5,
                color: AppColors.textMuted,
              ),
            ),
            const RegistrationCross(size: 22),
          ],
        ),
      ),
    );

    int i = 0;
    final total = candidates.length;

    while (i < total) {
      final pattern = (i ~/ 2) % 4;

      if (pattern == 0 && i + 1 < total) {
        // Pattern 0: Asymmetric Split Pair (Left Large, Right Staggered)
        final c1 = candidates[i];
        final c2 = candidates[i + 1];
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 50),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                SpatialResumePlate(
                  candidate: c1,
                  width: 480,
                  initialTiltDegrees: -1.2,
                  onTap: () => onSelectCandidate(c1),
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 80),
                  child: SpatialResumePlate(
                    candidate: c2,
                    width: 430,
                    initialTiltDegrees: 1.5,
                    onTap: () => onSelectCandidate(c2),
                  ),
                ),
              ],
            ),
          ),
        );
        i += 2;
      } else if (pattern == 1) {
        // Pattern 1: Solitary Panoramic Centerpiece with generous whitespace
        final c = candidates[i];
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 90),
            child: Stack(
              alignment: Alignment.center,
              children: [
                Positioned(
                  left: 60,
                  child: const RegistrationCross(size: 24),
                ),
                Positioned(
                  right: 60,
                  child: const RegistrationCross(size: 24),
                ),
                SpatialResumePlate(
                  candidate: c,
                  width: 520,
                  initialTiltDegrees: 0.0,
                  onTap: () => onSelectCandidate(c),
                ),
              ],
            ),
          ),
        );
        i += 1;
      } else if (pattern == 2 && i + 1 < total) {
        // Pattern 2: Offset Right Stagger (First shifted right, second shifted far left)
        final c1 = candidates[i];
        final c2 = candidates[i + 1];
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 60),
            child: Column(
              children: [
                Align(
                  alignment: const Alignment(0.65, 0),
                  child: SpatialResumePlate(
                    candidate: c1,
                    width: 450,
                    initialTiltDegrees: 1.6,
                    onTap: () => onSelectCandidate(c1),
                  ),
                ),
                const SizedBox(height: 70),
                Align(
                  alignment: const Alignment(-0.65, 0),
                  child: SpatialResumePlate(
                    candidate: c2,
                    width: 470,
                    initialTiltDegrees: -1.4,
                    onTap: () => onSelectCandidate(c2),
                  ),
                ),
              ],
            ),
          ),
        );
        i += 2;
      } else {
        // Pattern 3: Single Floating Plate with asymmetrical margin
        final c = candidates[i];
        final isEven = i % 2 == 0;
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 80, vertical: 70),
            child: Align(
              alignment: isEven ? const Alignment(-0.4, 0) : const Alignment(0.4, 0),
              child: SpatialResumePlate(
                candidate: c,
                width: 480,
                initialTiltDegrees: isEven ? -1.0 : 1.2,
                onTap: () => onSelectCandidate(c),
              ),
            ),
          ),
        );
        i += 1;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: children,
    );
  }

  Widget _buildMobileResponsiveFlow(BuildContext context, double screenWidth) {
    final plateWidth = (screenWidth - 48).clamp(320.0, 520.0);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 24),
      child: Column(
        children: candidates.asMap().entries.map((entry) {
          final idx = entry.key;
          final candidate = entry.value;
          final tilt = idx % 2 == 0 ? -1.0 : 1.0;

          return Padding(
            padding: const EdgeInsets.only(bottom: 48),
            child: SpatialResumePlate(
              candidate: candidate,
              width: plateWidth,
              initialTiltDegrees: tilt,
              onTap: () => onSelectCandidate(candidate),
            ),
          );
        }).toList(),
      ),
    );
  }
}
