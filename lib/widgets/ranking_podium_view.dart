import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import 'registration_cross.dart';

typedef OnSelectCandidate = void Function(Candidate candidate);

/// Architectural editorial Top 3 Candidate Ranking Podium.
/// Strictly adheres to the Camille Mormal dark editorial design system:
/// zero gaming tropes, zero trophy icons, zero cheesy gold/silver gradients.
class RankingPodiumView extends StatefulWidget {
  final List<Candidate> candidates;
  final OnSelectCandidate onSelectCandidate;
  final VoidCallback onClose;

  const RankingPodiumView({
    super.key,
    required this.candidates,
    required this.onSelectCandidate,
    required this.onClose,
  });

  @override
  State<RankingPodiumView> createState() => _RankingPodiumViewState();
}

class _RankingPodiumViewState extends State<RankingPodiumView>
    with SingleTickerProviderStateMixin {
  bool _isEvaluating = true;
  late final AnimationController _evalController;
  Timer? _evalTimer;

  @override
  void initState() {
    super.initState();
    _evalController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..forward();

    _evalTimer = Timer(const Duration(milliseconds: 900), () {
      if (mounted) {
        setState(() => _isEvaluating = false);
      }
    });
  }

  @override
  void dispose() {
    _evalController.dispose();
    _evalTimer?.cancel();
    super.dispose();
  }

  List<Candidate> get _sortedCandidates {
    final list = List<Candidate>.from(widget.candidates);
    list.sort((a, b) => b.matchScore.compareTo(a.matchScore));
    return list;
  }

  @override
  Widget build(BuildContext context) {
    final sorted = _sortedCandidates;
    final top1 = sorted.isNotEmpty ? sorted[0] : null;
    final top2 = sorted.length > 1 ? sorted[1] : null;
    final top3 = sorted.length > 2 ? sorted[2] : null;
    final remaining = sorted.length > 3 ? sorted.sublist(3) : <Candidate>[];

    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 900;
    final paddingH = isCompact ? 20.0 : 44.0;

    return Focus(
      autofocus: true,
      onKeyEvent: (node, event) {
        if (event is KeyDownEvent &&
            event.logicalKey == LogicalKeyboardKey.escape) {
          widget.onClose();
          return KeyEventResult.handled;
        }
        return KeyEventResult.ignored;
      },
      child: Container(
        color: AppColors.canvas.withValues(alpha: 0.98),
        child: _isEvaluating
            ? _buildEvaluatingState()
            : _buildPodiumContent(
                context,
                top1: top1,
                top2: top2,
                top3: top3,
                remaining: remaining,
                paddingH: paddingH,
                isCompact: isCompact,
              ),
      ),
    );
  }

  Widget _buildEvaluatingState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const RegistrationCross(size: 28),
          const SizedBox(height: 28),
          Text(
            'SYNCHRONIZING CANDIDATE ARCHIVES',
            style: GoogleFonts.syne(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
              color: AppColors.textWhite,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '// EVALUATING DOSSIERS · COMPUTING COMPOSITE MATCH VECTORS',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  letterSpacing: 1.2,
                  color: AppColors.emerald,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: 240,
            child: AnimatedBuilder(
              animation: _evalController,
              builder: (context, child) {
                return LinearProgressIndicator(
                  value: _evalController.value,
                  backgroundColor: AppColors.hairlineSubtle,
                  color: AppColors.emerald,
                  minHeight: 1.5,
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPodiumContent(
    BuildContext context, {
    required Candidate? top1,
    required Candidate? top2,
    required Candidate? top3,
    required List<Candidate> remaining,
    required double paddingH,
    required bool isCompact,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Top Podium Navigation Bar
        Container(
          padding: EdgeInsets.symmetric(horizontal: paddingH, vertical: 16),
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: AppColors.hairlineSubtle,
                width: 0.8,
              ),
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'NEXORA',
                    style: GoogleFonts.syne(
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 2.0,
                      color: AppColors.textWhite,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '// CANDIDATE RANKING PODIUM',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1.2,
                      color: AppColors.emerald,
                    ),
                  ),
                ],
              ),
              MouseRegion(
                cursor: SystemMouseCursors.click,
                child: GestureDetector(
                  onTap: widget.onClose,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                    decoration: BoxDecoration(
                      color: AppColors.plate,
                      border: Border.all(
                        color: AppColors.hairlineActive,
                        width: 0.8,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.arrow_back,
                          size: 13,
                          color: AppColors.textWhite,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'RETURN TO ARCHIVE [ESC]',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 10.5,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.8,
                            color: AppColors.textWhite,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Scrollable Podium & Extended Ranking Area
        Expanded(
          child: SingleChildScrollView(
            padding: EdgeInsets.symmetric(horizontal: paddingH, vertical: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header Titles
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'TOP CANDIDATES // COMPOSITE MATCH INDEX',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 10.5,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 1.5,
                            color: AppColors.textMuted,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'THE CANDIDATE PODIUM',
                          style: GoogleFonts.syne(
                            fontSize: isCompact ? 24 : 32,
                            fontWeight: FontWeight.w800,
                            letterSpacing: -0.8,
                            color: AppColors.textWhite,
                          ),
                        ),
                      ],
                    ),
                    Text(
                      '${widget.candidates.length} DOSSIERS RANKED',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.0,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                // Hairline Divider
                Container(
                  height: 0.8,
                  color: AppColors.hairlineSubtle,
                ),

                const SizedBox(height: 32),

                // THE TOP 3 ARCHITECTURAL PODIUM
                if (top1 != null)
                  isCompact
                      ? _buildCompactPodium(top1, top2, top3)
                      : _buildDesktopPodium(top1, top2, top3),

                const SizedBox(height: 48),

                // Extended Ranking Section Header
                if (remaining.isNotEmpty) ...[
                  Row(
                    children: [
                      Text(
                        '// EXTENDED DOSSIER ROSTER',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.2,
                          color: AppColors.textMuted,
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Container(
                          height: 0.8,
                          color: AppColors.hairlineSubtle,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  // Remaining Ranked Candidates Table
                  ...remaining.asMap().entries.map((entry) {
                    final rank = entry.key + 4;
                    final candidate = entry.value;
                    return _buildRankedRow(rank, candidate);
                  }),
                ],

                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDesktopPodium(Candidate top1, Candidate? top2, Candidate? top3) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // 2ND PLACE (Left - Subordinate)
        if (top2 != null)
          Expanded(
            child: _PodiumColumn(
              rank: 2,
              candidate: top2,
              isDominant: false,
              pedestalHeight: 64.0,
              onTap: () => widget.onSelectCandidate(top2),
            ),
          )
        else
          const Spacer(),

        const SizedBox(width: 20),

        // 1ST PLACE (Center - Dominant)
        Expanded(
          flex: 1,
          child: _PodiumColumn(
            rank: 1,
            candidate: top1,
            isDominant: true,
            pedestalHeight: 116.0,
            onTap: () => widget.onSelectCandidate(top1),
          ),
        ),

        const SizedBox(width: 20),

        // 3RD PLACE (Right - Subordinate)
        if (top3 != null)
          Expanded(
            child: _PodiumColumn(
              rank: 3,
              candidate: top3,
              isDominant: false,
              pedestalHeight: 38.0,
              onTap: () => widget.onSelectCandidate(top3),
            ),
          )
        else
          const Spacer(),
      ],
    );
  }

  Widget _buildCompactPodium(Candidate top1, Candidate? top2, Candidate? top3) {
    return Column(
      children: [
        _PodiumColumn(
          rank: 1,
          candidate: top1,
          isDominant: true,
          pedestalHeight: 36.0,
          onTap: () => widget.onSelectCandidate(top1),
        ),
        if (top2 != null) ...[
          const SizedBox(height: 16),
          _PodiumColumn(
            rank: 2,
            candidate: top2,
            isDominant: false,
            pedestalHeight: 24.0,
            onTap: () => widget.onSelectCandidate(top2),
          ),
        ],
        if (top3 != null) ...[
          const SizedBox(height: 16),
          _PodiumColumn(
            rank: 3,
            candidate: top3,
            isDominant: false,
            pedestalHeight: 24.0,
            onTap: () => widget.onSelectCandidate(top3),
          ),
        ],
      ],
    );
  }

  Widget _buildRankedRow(int rank, Candidate candidate) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => widget.onSelectCandidate(candidate),
        child: Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          decoration: BoxDecoration(
            color: AppColors.plate,
            border: Border.all(
              color: AppColors.hairlineSubtle,
              width: 0.8,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '#${rank.toString().padLeft(2, '0')}',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textMuted,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        candidate.name,
                        style: GoogleFonts.syne(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textWhite,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${candidate.headline} · ${candidate.category.toUpperCase()}',
                        style: GoogleFonts.spaceGrotesk(
                          fontSize: 11,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '${candidate.matchScore}%',
                    style: GoogleFonts.syne(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textWhite,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Text(
                    'VIEW [→]',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.8,
                      color: AppColors.emerald,
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

class _PodiumColumn extends StatefulWidget {
  final int rank;
  final Candidate candidate;
  final bool isDominant;
  final double pedestalHeight;
  final VoidCallback onTap;

  const _PodiumColumn({
    required this.rank,
    required this.candidate,
    required this.isDominant,
    required this.pedestalHeight,
    required this.onTap,
  });

  @override
  State<_PodiumColumn> createState() => _PodiumColumnState();
}

class _PodiumColumnState extends State<_PodiumColumn> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final candidate = widget.candidate;
    final isDom = widget.isDominant;
    final rank = widget.rank;

    final borderColor = isDom
        ? AppColors.hairlineActive
        : (_isHovered ? AppColors.hairlineActive : AppColors.hairlineSubtle);

    final rankLabel = rank == 1
        ? '#01 // HIGHEST MATCH'
        : (rank == 2 ? '#02 // SECOND POSITION' : '#03 // THIRD POSITION');

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Candidate Card Plate
            Container(
              padding: EdgeInsets.all(isDom ? 24.0 : 20.0),
              decoration: BoxDecoration(
                color: isDom
                    ? AppColors.plateElevated
                    : (_isHovered ? AppColors.plateHover : AppColors.plate),
                border: Border.all(
                  color: borderColor,
                  width: isDom ? 1.0 : 0.8,
                ),
                boxShadow: isDom
                    ? [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.7),
                          blurRadius: 32,
                          offset: const Offset(0, 16),
                        ),
                        BoxShadow(
                          color: AppColors.emerald.withValues(alpha: 0.08),
                          blurRadius: 36,
                          spreadRadius: 2,
                        ),
                      ]
                    : [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.4),
                          blurRadius: 18,
                          offset: const Offset(0, 8),
                        ),
                      ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Meta Row: Rank Indicator & Score
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        rankLabel,
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: isDom ? 11 : 9.5,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.0,
                          color: isDom ? AppColors.emerald : AppColors.textMuted,
                        ),
                      ),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.baseline,
                        textBaseline: TextBaseline.alphabetic,
                        children: [
                          Text(
                            '${candidate.matchScore}',
                            style: GoogleFonts.syne(
                              fontSize: isDom ? 26 : 22,
                              fontWeight: FontWeight.w800,
                              color: isDom ? AppColors.emerald : AppColors.textWhite,
                            ),
                          ),
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

                  SizedBox(height: isDom ? 18 : 14),

                  // Candidate Name
                  Text(
                    candidate.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.syne(
                      fontSize: isDom ? 23 : 19,
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.5,
                      color: AppColors.textWhite,
                    ),
                  ),

                  const SizedBox(height: 4),

                  // Headline Role
                  Text(
                    candidate.headline,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: isDom ? 13 : 12,
                      fontWeight: FontWeight.w400,
                      color: AppColors.textMuted,
                    ),
                  ),

                  SizedBox(height: isDom ? 14 : 10),

                  // Category and Experience Tag
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.canvas,
                      border: Border.all(
                        color: AppColors.hairline,
                        width: 0.6,
                      ),
                    ),
                    child: Text(
                      '${candidate.category.toUpperCase()} · ${candidate.yearsOfExperience}Y EXP',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 9.5,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.8,
                        color: AppColors.textWhite.withValues(alpha: 0.85),
                      ),
                    ),
                  ),

                  SizedBox(height: isDom ? 18 : 14),

                  // Skills Row
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: candidate.skills.take(3).map((skill) {
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.canvas,
                          border: Border.all(color: AppColors.hairlineSubtle, width: 0.6),
                        ),
                        child: Text(
                          skill.toUpperCase(),
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 9,
                            fontWeight: FontWeight.w500,
                            color: AppColors.textMuted,
                          ),
                        ),
                      );
                    }).toList(),
                  ),

                  SizedBox(height: isDom ? 20 : 16),

                  // Action Button
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
                        Text(
                          'FULL DOSSIER',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.0,
                            color: isDom || _isHovered
                                ? AppColors.emerald
                                : AppColors.textWhite,
                          ),
                        ),
                        Icon(
                          Icons.arrow_outward,
                          size: 13,
                          color: isDom || _isHovered
                              ? AppColors.emerald
                              : AppColors.textWhite,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Architectural Pedestal Block
            Container(
              height: widget.pedestalHeight,
              decoration: BoxDecoration(
                color: isDom
                    ? AppColors.plate.withValues(alpha: 0.6)
                    : AppColors.canvas.withValues(alpha: 0.8),
                border: Border(
                  left: BorderSide(color: borderColor, width: isDom ? 1.0 : 0.8),
                  right: BorderSide(color: borderColor, width: isDom ? 1.0 : 0.8),
                  bottom: BorderSide(color: borderColor, width: isDom ? 1.0 : 0.8),
                ),
              ),
              child: Center(
                child: Text(
                  'PODIUM · POSITION 0$rank',
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.5,
                    color: isDom ? AppColors.emerald : AppColors.textMuted,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
