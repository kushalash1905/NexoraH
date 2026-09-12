import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import 'candidate_preview_miniature.dart';

class SpatialResumePlate extends StatefulWidget {
  final Candidate candidate;
  final VoidCallback onTap;
  final double initialTiltDegrees;
  final double width;

  const SpatialResumePlate({
    super.key,
    required this.candidate,
    required this.onTap,
    this.initialTiltDegrees = 0.0,
    this.width = 460.0,
  });

  @override
  State<SpatialResumePlate> createState() => _SpatialResumePlateState();
}

class _SpatialResumePlateState extends State<SpatialResumePlate> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final candidate = widget.candidate;
    final currentTilt = _isHovered ? 0.0 : widget.initialTiltDegrees;
    final tiltRadians = currentTilt * (math.pi / 180.0);

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedRotation(
          duration: const Duration(milliseconds: 320),
          curve: Curves.easeOutCubic,
          turns: tiltRadians / (2 * math.pi),
          child: AnimatedSlide(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOutCubic,
            offset: Offset(0, _isHovered ? -0.02 : 0.0),
            child: AnimatedScale(
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOutCubic,
              scale: _isHovered ? 1.02 : 1.0,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 280),
                curve: Curves.easeOutCubic,
                width: widget.width,
                decoration: BoxDecoration(
                  color: _isHovered ? AppColors.plateHover : AppColors.plate,
                  border: Border.all(
                    color: _isHovered
                        ? AppColors.hairlineActive
                        : AppColors.hairline,
                    width: 0.8,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: _isHovered ? 0.75 : 0.4),
                      blurRadius: _isHovered ? 48 : 24,
                      spreadRadius: _isHovered ? 2 : 0,
                      offset: Offset(0, _isHovered ? 24 : 12),
                    ),
                    if (_isHovered)
                      BoxShadow(
                        color: AppColors.emerald.withValues(alpha: 0.06),
                        blurRadius: 36,
                        spreadRadius: 4,
                      ),
                  ],
                ),
                child: Stack(
                  children: [
                    // Giant Faint Watermark Sequence Number behind content
                    Positioned(
                      right: 18,
                      top: 14,
                      child: IgnorePointer(
                        child: Text(
                          candidate.formattedNumber,
                          style: GoogleFonts.syne(
                            fontSize: 88,
                            fontWeight: FontWeight.w800,
                            letterSpacing: -4.0,
                            color: Colors.white.withValues(alpha: 0.035),
                          ),
                        ),
                      ),
                    ),

                    // Main Content Body
                    Padding(
                      padding: const EdgeInsets.all(26.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // Top Meta Row: Index & Category & Match Indicator
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Text(
                                          candidate.formattedNumber,
                                          style: GoogleFonts.jetBrainsMono(
                                            fontSize: 12,
                                            fontWeight: FontWeight.w700,
                                            letterSpacing: 1.0,
                                            color: _isHovered
                                                ? AppColors.emerald
                                                : AppColors.textWhite,
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          '//',
                                          style: GoogleFonts.jetBrainsMono(
                                            fontSize: 11,
                                            color: AppColors.textMuted,
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Flexible(
                                          child: Text(
                                            candidate.category.toUpperCase(),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: GoogleFonts.jetBrainsMono(
                                              fontSize: 10,
                                              fontWeight: FontWeight.w600,
                                              letterSpacing: 1.0,
                                              color: AppColors.textMuted,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),

                              // Editorial Match Score Treatment
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.baseline,
                                textBaseline: TextBaseline.alphabetic,
                                children: [
                                  Text(
                                    '${candidate.matchScore}',
                                    style: GoogleFonts.syne(
                                      fontSize: 22,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: -0.5,
                                      color: candidate.matchScore >= 90
                                          ? AppColors.emerald
                                          : AppColors.textWhite,
                                    ),
                                  ),
                                  const SizedBox(width: 3),
                                  Text(
                                    '%',
                                    style: GoogleFonts.jetBrainsMono(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w700,
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),

                          const SizedBox(height: 18),

                          // Candidate Name in high-impact typography
                          Text(
                            candidate.name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: GoogleFonts.syne(
                              fontSize: 24,
                              fontWeight: FontWeight.w700,
                              letterSpacing: -0.6,
                              color: _isHovered
                                  ? AppColors.textWhite
                                  : AppColors.textWhite.withValues(alpha: 0.95),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            candidate.headline,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: GoogleFonts.spaceGrotesk(
                              fontSize: 13,
                              fontWeight: FontWeight.w400,
                              color: AppColors.textMuted,
                            ),
                          ),

                          const SizedBox(height: 20),

                          // Miniature Resume Document preview
                          SizedBox(
                            height: 154,
                            width: double.infinity,
                            child: CandidatePreviewMiniature(
                              candidate: candidate,
                              isHovered: _isHovered,
                            ),
                          ),

                          const SizedBox(height: 18),

                          // Key Skills Tags
                          Wrap(
                            spacing: 6,
                            runSpacing: 6,
                            children: candidate.skills.take(3).map((skill) {
                              return Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 3.5,
                                ),
                                decoration: BoxDecoration(
                                  color: AppColors.canvas,
                                  border: Border.all(
                                    color: AppColors.hairline,
                                    width: 0.6,
                                  ),
                                ),
                                child: Text(
                                  skill.toUpperCase(),
                                  style: GoogleFonts.jetBrainsMono(
                                    fontSize: 9.5,
                                    fontWeight: FontWeight.w600,
                                    letterSpacing: 0.6,
                                    color: AppColors.textWhite.withValues(alpha: 0.75),
                                  ),
                                ),
                              );
                            }).toList(),
                          ),

                          const SizedBox(height: 22),

                          // Bottom Coordinate Bar
                          Container(
                            padding: const EdgeInsets.only(top: 12),
                            decoration: const BoxDecoration(
                              border: Border(
                                top: BorderSide(
                                  color: AppColors.hairlineSubtle,
                                  width: 0.8,
                                ),
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    '${candidate.location.toUpperCase()} · ${candidate.yearsOfExperience}Y EXP',
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: GoogleFonts.jetBrainsMono(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w500,
                                      letterSpacing: 0.8,
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Row(
                                  children: [
                                    Text(
                                      'DOSSIER',
                                      style: GoogleFonts.jetBrainsMono(
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 1.0,
                                        color: _isHovered
                                            ? AppColors.emerald
                                            : AppColors.textWhite,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    Icon(
                                      Icons.arrow_outward,
                                      size: 13,
                                      color: _isHovered
                                          ? AppColors.emerald
                                          : AppColors.textWhite,
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
