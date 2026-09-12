import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import 'candidate_preview_miniature.dart';

/// Clean, symmetric, straight resume card for the horizontal carousel.
/// Free of random rotations, tilted cards, or uneven positioning.
class CarouselResumeCard extends StatefulWidget {
  final Candidate candidate;
  final bool isFocused;
  final double focusFactor; // 0.0 (off-center) to 1.0 (dead center)
  final double cardWidth;
  final double cardHeight;
  final VoidCallback onTap;
  final VoidCallback? onOpenDetail;

  const CarouselResumeCard({
    super.key,
    required this.candidate,
    required this.isFocused,
    this.focusFactor = 0.0,
    this.cardWidth = 420.0,
    this.cardHeight = 440.0,
    required this.onTap,
    this.onOpenDetail,
  });

  @override
  State<CarouselResumeCard> createState() => _CarouselResumeCardState();
}

class _CarouselResumeCardState extends State<CarouselResumeCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final candidate = widget.candidate;
    final isCenter = widget.isFocused;
    final isHighlighted = isCenter || _isHovered;
    final factor = widget.focusFactor.clamp(0.0, 1.0);

    // Smoothly interpolated styling based on focus factor
    final borderColor = Color.lerp(
      _isHovered ? AppColors.hairlineActive : AppColors.hairline,
      AppColors.hairlineActive,
      factor,
    )!;

    final baseShadowColor = Colors.black.withValues(alpha: 0.35 + (0.45 * factor));
    final blurRadius = 18.0 + (26.0 * factor);
    final offsetY = 8.0 + (12.0 * factor);

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: Container(
          width: widget.cardWidth,
          height: widget.cardHeight,
          decoration: BoxDecoration(
            color: isHighlighted ? AppColors.plateHover : AppColors.plate,
            border: Border.all(
              color: borderColor,
              width: isCenter ? 1.0 : 0.8,
            ),
            boxShadow: [
              BoxShadow(
                color: baseShadowColor,
                blurRadius: blurRadius,
                spreadRadius: isCenter ? 1 : 0,
                offset: Offset(0, offsetY),
              ),
              if (factor > 0.05)
                BoxShadow(
                  color: AppColors.emerald.withValues(alpha: 0.08 * factor),
                  blurRadius: 36,
                  spreadRadius: 2,
                ),
            ],
          ),
          child: Stack(
            children: [
              // Faint watermark sequence number behind content
              Positioned(
                right: 18,
                top: 14,
                child: IgnorePointer(
                  child: Text(
                    candidate.formattedNumber,
                    style: GoogleFonts.syne(
                      fontSize: 84,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -4.0,
                      color: Colors.white.withValues(alpha: 0.02 + (0.03 * factor)),
                    ),
                  ),
                ),
              ),

              // Card Content
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 22.0, vertical: 20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Top Meta Row: Index & Category & Match Score
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Expanded(
                          child: Row(
                            children: [
                              Text(
                                candidate.formattedNumber,
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 1.0,
                                  color: isHighlighted
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
                        ),
                        const SizedBox(width: 8),
                        // Match Score
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
                            const SizedBox(width: 2),
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

                    const SizedBox(height: 14),

                    // Candidate Name & Headline
                    Text(
                      candidate.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: GoogleFonts.syne(
                        fontSize: 21,
                        fontWeight: FontWeight.w700,
                        letterSpacing: -0.5,
                        color: isHighlighted
                            ? AppColors.textWhite
                            : AppColors.textWhite.withValues(alpha: 0.9),
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      candidate.headline,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 12,
                        fontWeight: FontWeight.w400,
                        color: AppColors.textMuted,
                      ),
                    ),

                    const SizedBox(height: 14),

                    // Miniature Resume Preview
                    SizedBox(
                      height: 136,
                      width: double.infinity,
                      child: CandidatePreviewMiniature(
                        candidate: candidate,
                        isHovered: isHighlighted,
                      ),
                    ),

                    const SizedBox(height: 14),

                    // Skills Tags (Consistent single row)
                    SizedBox(
                      height: 26,
                      child: ListView(
                        scrollDirection: Axis.horizontal,
                        physics: const NeverScrollableScrollPhysics(),
                        children: candidate.skills.take(3).map((skill) {
                          return Container(
                            margin: const EdgeInsets.only(right: 6),
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
                            child: Center(
                              child: Text(
                                skill.toUpperCase(),
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 0.6,
                                  color: AppColors.textWhite.withValues(alpha: 0.8),
                                ),
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ),

                    const Spacer(),

                    // Bottom Bar
                    Container(
                      padding: const EdgeInsets.only(top: 10),
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
                                fontSize: 9.5,
                                fontWeight: FontWeight.w500,
                                letterSpacing: 0.8,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          MouseRegion(
                            cursor: SystemMouseCursors.click,
                            child: GestureDetector(
                              onTap: widget.onOpenDetail ?? widget.onTap,
                              child: Row(
                                children: [
                                  Text(
                                    'OPEN DOSSIER',
                                    style: GoogleFonts.jetBrainsMono(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 1.0,
                                      color: isHighlighted
                                          ? AppColors.emerald
                                          : AppColors.textWhite,
                                    ),
                                  ),
                                  const SizedBox(width: 4),
                                  Icon(
                                    Icons.arrow_outward,
                                    size: 12,
                                    color: isHighlighted
                                        ? AppColors.emerald
                                        : AppColors.textWhite,
                                  ),
                                ],
                              ),
                            ),
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
    );
  }
}
