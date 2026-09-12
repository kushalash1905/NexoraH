import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';

class CandidatePreviewMiniature extends StatelessWidget {
  final Candidate candidate;
  final bool isHovered;

  const CandidatePreviewMiniature({
    super.key,
    required this.candidate,
    this.isHovered = false,
  });

  @override
  Widget build(BuildContext context) {
    final initials = candidate.name
        .split(' ')
        .take(2)
        .map((w) => w.isNotEmpty ? w[0] : '')
        .join();

    return AnimatedContainer(
      duration: const Duration(milliseconds: 280),
      curve: Curves.easeOutCubic,
      decoration: BoxDecoration(
        color: AppColors.paper,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: isHovered
              ? AppColors.emerald.withValues(alpha: 0.6)
              : AppColors.paperBorder,
          width: isHovered ? 1.2 : 1.0,
        ),
        boxShadow: [
          BoxShadow(
            color: isHovered
                ? Colors.black.withValues(alpha: 0.45)
                : Colors.black.withValues(alpha: 0.25),
            blurRadius: isHovered ? 14 : 6,
            offset: Offset(0, isHovered ? 8 : 3),
          ),
          if (isHovered)
            BoxShadow(
              color: AppColors.emerald.withValues(alpha: 0.12),
              blurRadius: 18,
              spreadRadius: 1,
            ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(3),
        child: Stack(
          children: [
            // Background watermark index number
            Positioned(
              right: 8,
              bottom: 4,
              child: Text(
                candidate.formattedNumber,
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppColors.inkPrimary.withValues(alpha: 0.05),
                ),
              ),
            ),
            // Scaled miniature resume document content
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Document mini header
                  Row(
                    children: [
                      // Monogram badge
                      Container(
                        width: 22,
                        height: 22,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: AppColors.inkPrimary,
                          borderRadius: BorderRadius.circular(2),
                        ),
                        child: Text(
                          initials,
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            color: AppColors.paper,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              candidate.name.toUpperCase(),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: GoogleFonts.syne(
                                fontSize: 9.5,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.5,
                                color: AppColors.inkPrimary,
                              ),
                            ),
                            Text(
                              candidate.headline,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: GoogleFonts.spaceGrotesk(
                                fontSize: 7.5,
                                fontWeight: FontWeight.w500,
                                color: AppColors.inkMuted,
                              ),
                            ),
                          ],
                        ),
                      ),
                      // Match score stamp
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 4.5, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.inkPrimary.withValues(alpha: 0.06),
                          borderRadius: BorderRadius.circular(2),
                        ),
                        child: Text(
                          '${candidate.matchScore}%',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 8.5,
                            fontWeight: FontWeight.w700,
                            color: AppColors.inkPrimary,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Container(
                    height: 0.8,
                    color: AppColors.inkDivider,
                  ),
                  const SizedBox(height: 8),

                  // Mini two-column resume body representation
                  Expanded(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Left column (Main content skeleton)
                        Expanded(
                          flex: 5,
                          child: ClipRect(
                            child: SingleChildScrollView(
                              physics: const NeverScrollableScrollPhysics(),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Summary snippet line
                                  Text(
                                    candidate.previewSnippet,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: GoogleFonts.inter(
                                      fontSize: 7.5,
                                      height: 1.25,
                                      fontWeight: FontWeight.w400,
                                      color: AppColors.inkSecondary,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  // Experience section label
                                  Text(
                                    'EXPERIENCE',
                                    style: GoogleFonts.jetBrainsMono(
                                      fontSize: 6.5,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 0.6,
                                      color: AppColors.inkMuted,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  if (candidate.experiences.isNotEmpty) ...[
                                    Text(
                                      '${candidate.experiences.first.role} · ${candidate.experiences.first.company}',
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: GoogleFonts.inter(
                                        fontSize: 7.0,
                                        fontWeight: FontWeight.w600,
                                        color: AppColors.inkPrimary,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    if (candidate.experiences.first.bullets.isNotEmpty)
                                      Text(
                                        '• ${candidate.experiences.first.bullets.first}',
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: GoogleFonts.inter(
                                          fontSize: 6.5,
                                          height: 1.2,
                                          color: AppColors.inkSecondary,
                                        ),
                                      ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Right column (Mini sidebar)
                        Expanded(
                          flex: 3,
                          child: Container(
                            padding: const EdgeInsets.only(left: 6),
                            decoration: const BoxDecoration(
                              border: Border(
                                left: BorderSide(
                                  color: AppColors.inkDivider,
                                  width: 0.6,
                                ),
                              ),
                            ),
                            child: ClipRect(
                              child: SingleChildScrollView(
                                physics: const NeverScrollableScrollPhysics(),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'SKILLS',
                                      style: GoogleFonts.jetBrainsMono(
                                        fontSize: 6.5,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 0.6,
                                        color: AppColors.inkMuted,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    ...candidate.skills.take(4).map(
                                          (skill) => Padding(
                                            padding: const EdgeInsets.only(bottom: 2.5),
                                            child: Text(
                                              skill,
                                              maxLines: 1,
                                              overflow: TextOverflow.ellipsis,
                                              style: GoogleFonts.spaceGrotesk(
                                                fontSize: 6.5,
                                                fontWeight: FontWeight.w500,
                                                color: AppColors.inkPrimary,
                                              ),
                                            ),
                                          ),
                                        ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Bottom mini archival stamp
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'DOSSIER VERIFIED',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 6.0,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 0.6,
                          color: AppColors.inkMuted,
                        ),
                      ),
                      Text(
                        '${candidate.yearsOfExperience}Y EXP',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 6.0,
                          fontWeight: FontWeight.w700,
                          color: AppColors.inkPrimary,
                        ),
                      ),
                    ],
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
