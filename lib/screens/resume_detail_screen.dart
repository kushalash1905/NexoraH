import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import '../widgets/registration_cross.dart';
import '../widgets/resume_document.dart';

class ResumeDetailScreen extends StatefulWidget {
  final List<Candidate> candidates;
  final int initialIndex;

  const ResumeDetailScreen({
    super.key,
    required this.candidates,
    required this.initialIndex,
  });

  @override
  State<ResumeDetailScreen> createState() => _ResumeDetailScreenState();
}

class _ResumeDetailScreenState extends State<ResumeDetailScreen> {
  late int _currentIndex;
  late final ScrollController _scrollController;
  final Set<String> _shortlistedIds = {};
  bool _nextHovered = false;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
    _scrollController = ScrollController();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _nextCandidate() {
    if (_currentIndex < widget.candidates.length - 1) {
      setState(() => _currentIndex++);
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOutCubic,
      );
    }
  }

  void _prevCandidate() {
    if (_currentIndex > 0) {
      setState(() => _currentIndex--);
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOutCubic,
      );
    }
  }

  void _toggleShortlist(String id) {
    setState(() {
      if (_shortlistedIds.contains(id)) {
        _shortlistedIds.remove(id);
      } else {
        _shortlistedIds.add(id);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final candidate = widget.candidates[_currentIndex];
    final isShortlisted = _shortlistedIds.contains(candidate.id);
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 800;

    final hasNext = _currentIndex < widget.candidates.length - 1;
    final nextCandidate = hasNext ? widget.candidates[_currentIndex + 1] : null;

    return Focus(
      autofocus: true,
      onKeyEvent: (node, event) {
        if (event is KeyDownEvent) {
          if (event.logicalKey == LogicalKeyboardKey.escape) {
            Navigator.of(context).pop();
            return KeyEventResult.handled;
          } else if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
            _nextCandidate();
            return KeyEventResult.handled;
          } else if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
            _prevCandidate();
            return KeyEventResult.handled;
          }
        }
        return KeyEventResult.ignored;
      },
      child: Scaffold(
        backgroundColor: AppColors.canvas,
        body: Stack(
          children: [
            // Scrollable Document Layout with Camille Mormal Next Project Footer
            SingleChildScrollView(
              controller: _scrollController,
              padding: const EdgeInsets.only(top: 86, bottom: 60),
              child: Column(
                children: [
                  // Atmospheric Frame Header with registration crosses
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 20),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const RegistrationCross(size: 20),
                        Text(
                          '// PHYSICAL RECORD // ${candidate.id}',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 10.5,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 1.5,
                            color: AppColors.textMuted,
                          ),
                        ),
                        const RegistrationCross(size: 20),
                      ],
                    ),
                  ),

                  // The Physical Resume Sheet
                  ResumeDocument(candidate: candidate),

                  const SizedBox(height: 60),

                  // Camille Mormal Signature Next Project Footer (.w-footer)
                  if (hasNext && nextCandidate != null) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 80, horizontal: 32),
                      decoration: const BoxDecoration(
                        color: AppColors.plate,
                        border: Border(
                          top: BorderSide(color: AppColors.hairline, width: 0.8),
                        ),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'NEXT DOSSIER // ${( _currentIndex + 2).toString().padLeft(2, '0')}',
                            style: GoogleFonts.jetBrainsMono(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 2.0,
                              color: AppColors.textMuted,
                            ),
                          ),
                          const SizedBox(height: 14),
                          MouseRegion(
                            cursor: SystemMouseCursors.click,
                            onEnter: (_) => setState(() => _nextHovered = true),
                            onExit: (_) => setState(() => _nextHovered = false),
                            child: GestureDetector(
                              onTap: _nextCandidate,
                              child: Column(
                                children: [
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                        nextCandidate.name.toUpperCase(),
                                        style: GoogleFonts.syne(
                                          fontSize: isCompact ? 28 : 46,
                                          fontWeight: FontWeight.w800,
                                          letterSpacing: -1.2,
                                          color: _nextHovered
                                              ? AppColors.emerald
                                              : AppColors.textWhite,
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                      Icon(
                                        Icons.arrow_forward_rounded,
                                        size: isCompact ? 24 : 38,
                                        color: _nextHovered
                                            ? AppColors.emerald
                                            : AppColors.textWhite,
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    '${nextCandidate.headline.toUpperCase()} · ${nextCandidate.matchScore}% MATCH RATING',
                                    style: GoogleFonts.jetBrainsMono(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w500,
                                      letterSpacing: 1.0,
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Fixed Top Editorial Navigation Bar (Camille Mormal .w-back & index)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: Container(
                padding: EdgeInsets.symmetric(
                  horizontal: isCompact ? 20 : 44,
                  vertical: 18,
                ),
                decoration: BoxDecoration(
                  color: AppColors.canvas.withValues(alpha: 0.96),
                  border: const Border(
                    bottom: BorderSide(
                      color: AppColors.hairlineSubtle,
                      width: 0.8,
                    ),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Back Link (Camille Mormal .w-back)
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () => Navigator.of(context).pop(),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.arrow_back,
                              size: 14,
                              color: AppColors.textWhite,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              isCompact ? 'INDEX' : 'RETURN TO ARCHIVE [ESC]',
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 1.0,
                                color: AppColors.textWhite,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    // Candidate Index Navigator (< 03 / 18 >)
                    Row(
                      children: [
                        _NavArrow(
                          icon: Icons.chevron_left,
                          isEnabled: _currentIndex > 0,
                          onTap: _prevCandidate,
                        ),
                        const SizedBox(width: 10),
                        Text(
                          '${(_currentIndex + 1).toString().padLeft(2, '0')} / ${widget.candidates.length.toString().padLeft(2, '0')}',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.0,
                            color: AppColors.textWhite,
                          ),
                        ),
                        const SizedBox(width: 10),
                        _NavArrow(
                          icon: Icons.chevron_right,
                          isEnabled: _currentIndex < widget.candidates.length - 1,
                          onTap: _nextCandidate,
                        ),
                      ],
                    ),

                    // Shortlist Action
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () => _toggleShortlist(candidate.id),
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: isShortlisted
                                ? AppColors.emerald.withValues(alpha: 0.15)
                                : Colors.transparent,
                            border: Border.all(
                              color: isShortlisted
                                  ? AppColors.emerald
                                  : AppColors.hairline,
                              width: 0.8,
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                isShortlisted ? Icons.bookmark : Icons.bookmark_border,
                                size: 13,
                                color: isShortlisted
                                    ? AppColors.emerald
                                    : AppColors.textWhite,
                              ),
                              if (!isCompact) ...[
                                const SizedBox(width: 6),
                                Text(
                                  isShortlisted ? 'SHORTLISTED' : 'SHORTLIST',
                                  style: GoogleFonts.jetBrainsMono(
                                    fontSize: 10.5,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.8,
                                    color: isShortlisted
                                        ? AppColors.emerald
                                        : AppColors.textWhite,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavArrow extends StatelessWidget {
  final IconData icon;
  final bool isEnabled;
  final VoidCallback onTap;

  const _NavArrow({
    required this.icon,
    required this.isEnabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: isEnabled ? SystemMouseCursors.click : SystemMouseCursors.basic,
      child: GestureDetector(
        onTap: isEnabled ? onTap : null,
        child: Container(
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            border: Border.all(
              color: isEnabled ? AppColors.hairline : AppColors.hairlineSubtle,
              width: 0.6,
            ),
          ),
          child: Icon(
            icon,
            size: 15,
            color: isEnabled ? AppColors.textWhite : AppColors.textMuted,
          ),
        ),
      ),
    );
  }
}
