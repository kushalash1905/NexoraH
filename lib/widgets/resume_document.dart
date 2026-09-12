import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';

class ResumeDocument extends StatelessWidget {
  final Candidate candidate;

  const ResumeDocument({
    super.key,
    required this.candidate,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 860),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
        decoration: BoxDecoration(
          color: AppColors.paper,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(color: AppColors.paperBorder, width: 1.2),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.55),
              blurRadius: 36,
              spreadRadius: 2,
              offset: const Offset(0, 16),
            ),
            BoxShadow(
              color: AppColors.emerald.withValues(alpha: 0.04),
              blurRadius: 50,
              spreadRadius: 8,
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 48),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Archival Classification Bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 7,
                        height: 7,
                        decoration: const BoxDecoration(
                          color: AppColors.inkPrimary,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'CANDIDATE DOSSIER · ${candidate.id}',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.2,
                          color: AppColors.inkMuted,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.inkPrimary,
                      borderRadius: BorderRadius.circular(2),
                    ),
                    child: Text(
                      '${candidate.matchScore}% MATCH SCORE',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 10.5,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.8,
                        color: AppColors.paper,
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              Container(height: 1.5, color: AppColors.inkPrimary),
              const SizedBox(height: 28),

              // Candidate Main Header
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          candidate.name,
                          style: GoogleFonts.syne(
                            fontSize: 34,
                            fontWeight: FontWeight.w700,
                            letterSpacing: -0.8,
                            color: AppColors.inkPrimary,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          candidate.headline,
                          style: GoogleFonts.spaceGrotesk(
                            fontSize: 16,
                            fontWeight: FontWeight.w500,
                            color: AppColors.inkSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Watermark sequence badge
                  Container(
                    width: 52,
                    height: 52,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      border: Border.all(color: AppColors.inkDivider, width: 1.5),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      candidate.formattedNumber,
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: AppColors.inkPrimary,
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Contact & Links Bar
              Wrap(
                spacing: 18,
                runSpacing: 8,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  _ContactItem(
                    icon: Icons.email_outlined,
                    label: candidate.email,
                  ),
                  _ContactItem(
                    icon: Icons.phone_outlined,
                    label: candidate.phone,
                  ),
                  _ContactItem(
                    icon: Icons.place_outlined,
                    label: candidate.location,
                  ),
                  _ContactItem(
                    icon: Icons.link_rounded,
                    label: candidate.portfolioUrl.replaceFirst('https://', ''),
                  ),
                  _ContactItem(
                    icon: Icons.code_rounded,
                    label: candidate.githubUrl.replaceFirst('https://', ''),
                  ),
                ],
              ),

              const SizedBox(height: 32),
              Container(height: 0.8, color: AppColors.inkDivider),
              const SizedBox(height: 28),

              // Section: Professional Summary
              _SectionHeading(title: 'PROFESSIONAL SUMMARY', number: '01'),
              const SizedBox(height: 12),
              Text(
                candidate.summary,
                style: GoogleFonts.inter(
                  fontSize: 13.5,
                  height: 1.65,
                  fontWeight: FontWeight.w400,
                  color: AppColors.inkPrimary,
                ),
              ),

              const SizedBox(height: 32),

              // Section: Core Competencies / Skills
              _SectionHeading(title: 'TECHNICAL COMPETENCIES & EXPERTISE', number: '02'),
              const SizedBox(height: 14),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: candidate.skills.map((skill) {
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: AppColors.paperSurface,
                      borderRadius: BorderRadius.circular(3),
                      border: Border.all(
                        color: AppColors.paperBorder,
                        width: 0.8,
                      ),
                    ),
                    child: Text(
                      skill,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.inkPrimary,
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 36),

              // Section: Professional Experience
              _SectionHeading(title: 'PROFESSIONAL EXPERIENCE', number: '03'),
              const SizedBox(height: 16),
              ...candidate.experiences.map((exp) => _ExperienceItem(experience: exp)),

              const SizedBox(height: 28),

              // Section: Key Projects
              if (candidate.projects.isNotEmpty) ...[
                _SectionHeading(title: 'FEATURED ARCHITECTURAL PROJECTS', number: '04'),
                const SizedBox(height: 16),
                ...candidate.projects.map((proj) => _ProjectItem(project: proj)),
                const SizedBox(height: 28),
              ],

              // Section: Education & Credentials
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 6,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _SectionHeading(title: 'EDUCATION & SCHOLARSHIP', number: '05'),
                        const SizedBox(height: 14),
                        ...candidate.education.map((edu) => _EducationItem(education: edu)),
                      ],
                    ),
                  ),
                  const SizedBox(width: 32),
                  if (candidate.certifications.isNotEmpty)
                    Expanded(
                      flex: 4,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _SectionHeading(title: 'CERTIFICATIONS', number: '06'),
                          const SizedBox(height: 14),
                          ...candidate.certifications.map((cert) => Padding(
                                padding: const EdgeInsets.only(bottom: 10),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Padding(
                                      padding: EdgeInsets.only(top: 4, right: 8),
                                      child: Icon(
                                        Icons.verified_outlined,
                                        size: 13,
                                        color: AppColors.inkPrimary,
                                      ),
                                    ),
                                    Expanded(
                                      child: Text(
                                        cert,
                                        style: GoogleFonts.inter(
                                          fontSize: 12.5,
                                          fontWeight: FontWeight.w500,
                                          height: 1.4,
                                          color: AppColors.inkPrimary,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              )),
                        ],
                      ),
                    ),
                ],
              ),

              const SizedBox(height: 40),
              Container(height: 1.0, color: AppColors.inkDivider),
              const SizedBox(height: 18),

              // Archival Document Footer Stamp
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'NEXORA VERIFIED ARCHIVE RECORD · HACKATHON EDITION',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 9.5,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.8,
                      color: AppColors.inkMuted,
                    ),
                  ),
                  Text(
                    'PAGE 01 / 01',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 9.5,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.8,
                      color: AppColors.inkMuted,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionHeading extends StatelessWidget {
  final String title;
  final String number;

  const _SectionHeading({
    required this.title,
    required this.number,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              number,
              style: GoogleFonts.jetBrainsMono(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.0,
                color: AppColors.inkMuted,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              title,
              style: GoogleFonts.syne(
                fontSize: 12.5,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.2,
                color: AppColors.inkPrimary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Container(
          height: 0.8,
          color: AppColors.inkDivider,
        ),
      ],
    );
  }
}

class _ContactItem extends StatelessWidget {
  final IconData icon;
  final String label;

  const _ContactItem({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 13, color: AppColors.inkMuted),
        const SizedBox(width: 6),
        Text(
          label,
          style: GoogleFonts.spaceGrotesk(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: AppColors.inkSecondary,
          ),
        ),
      ],
    );
  }
}

class _ExperienceItem extends StatelessWidget {
  final WorkExperience experience;

  const _ExperienceItem({required this.experience});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      experience.role,
                      style: GoogleFonts.syne(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: AppColors.inkPrimary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${experience.company} · ${experience.location}',
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: AppColors.inkSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.paperSurface,
                  borderRadius: BorderRadius.circular(2),
                  border: Border.all(color: AppColors.paperBorder, width: 0.8),
                ),
                child: Text(
                  experience.period,
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                    color: AppColors.inkPrimary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ...experience.bullets.map((bullet) => Padding(
                padding: const EdgeInsets.only(bottom: 5, left: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 6, right: 8),
                      child: Container(
                        width: 4,
                        height: 4,
                        decoration: const BoxDecoration(
                          color: AppColors.inkPrimary,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        bullet,
                        style: GoogleFonts.inter(
                          fontSize: 12.5,
                          height: 1.5,
                          fontWeight: FontWeight.w400,
                          color: AppColors.inkSecondary,
                        ),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}

class _ProjectItem extends StatelessWidget {
  final ResumeProject project;

  const _ProjectItem({required this.project});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppColors.paperSurface,
          borderRadius: BorderRadius.circular(3),
          border: Border.all(color: AppColors.paperBorder, width: 0.8),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  project.name,
                  style: GoogleFonts.syne(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: AppColors.inkPrimary,
                  ),
                ),
                if (project.link != null)
                  Text(
                    project.link!.replaceFirst('https://', ''),
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 10.5,
                      fontWeight: FontWeight.w600,
                      color: AppColors.inkMuted,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              project.description,
              style: GoogleFonts.inter(
                fontSize: 12,
                height: 1.45,
                color: AppColors.inkSecondary,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: project.techStack.map((tech) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.paper,
                    borderRadius: BorderRadius.circular(2),
                    border: Border.all(color: AppColors.paperBorder, width: 0.6),
                  ),
                  child: Text(
                    tech,
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 9.5,
                      fontWeight: FontWeight.w600,
                      color: AppColors.inkPrimary,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _EducationItem extends StatelessWidget {
  final Education education;

  const _EducationItem({required this.education});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  education.degree,
                  style: GoogleFonts.syne(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                    color: AppColors.inkPrimary,
                  ),
                ),
              ),
              Text(
                education.year,
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.inkMuted,
                ),
              ),
            ],
          ),
          const SizedBox(height: 3),
          Text(
            education.institution,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 12.5,
              fontWeight: FontWeight.w500,
              color: AppColors.inkSecondary,
            ),
          ),
          if (education.details != null) ...[
            const SizedBox(height: 3),
            Text(
              education.details!,
              style: GoogleFonts.inter(
                fontSize: 11.5,
                fontStyle: FontStyle.italic,
                color: AppColors.inkMuted,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
