import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../data/dummy_candidates.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import '../widgets/camille_nav_bar.dart';
import '../widgets/horizontal_resume_carousel.dart';
import '../widgets/registration_cross.dart';
import 'resume_detail_screen.dart';

class ResumeGalleryScreen extends StatefulWidget {
  const ResumeGalleryScreen({super.key});

  @override
  State<ResumeGalleryScreen> createState() => _ResumeGalleryScreenState();
}

class _ResumeGalleryScreenState extends State<ResumeGalleryScreen> {
  String _selectedCategory = 'ALL';
  String _sortBy = 'score'; // 'score', 'exp', 'index'
  String _searchQuery = '';

  final List<String> _categories = [
    'ALL',
    'Systems & Distributed',
    'AI & Machine Learning',
    'Creative & Frontend',
    'Cloud & Infrastructure',
    'Full-Stack & Web',
    'Mobile & Flutter',
    'Security & Cloud',
  ];

  List<Candidate> get _filteredCandidates {
    var list = dummyCandidates.where((c) {
      // Category filter
      if (_selectedCategory != 'ALL' && c.category != _selectedCategory) {
        return false;
      }
      // Search filter
      if (_searchQuery.trim().isNotEmpty) {
        final q = _searchQuery.toLowerCase();
        final matchesName = c.name.toLowerCase().contains(q);
        final matchesHeadline = c.headline.toLowerCase().contains(q);
        final matchesSkills = c.skills.any((s) => s.toLowerCase().contains(q));
        final matchesCategory = c.category.toLowerCase().contains(q);
        if (!matchesName && !matchesHeadline && !matchesSkills && !matchesCategory) {
          return false;
        }
      }
      return true;
    }).toList();

    // Sort
    if (_sortBy == 'score') {
      list.sort((a, b) => b.matchScore.compareTo(a.matchScore));
    } else if (_sortBy == 'exp') {
      list.sort((a, b) => b.yearsOfExperience.compareTo(a.yearsOfExperience));
    } else if (_sortBy == 'index') {
      list.sort((a, b) => a.candidateNumber.compareTo(b.candidateNumber));
    }

    return list;
  }

  void _openCandidateDetail(Candidate candidate, List<Candidate> currentList) {
    final indexInCurrentList = currentList.indexOf(candidate);
    Navigator.of(context).push(
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) {
          return ResumeDetailScreen(
            candidates: currentList,
            initialIndex: indexInCurrentList >= 0 ? indexInCurrentList : 0,
          );
        },
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          const begin = Offset(0.0, 0.03);
          const end = Offset.zero;
          final curve = CurvedAnimation(
            parent: animation,
            curve: Curves.easeOutCubic,
          );
          return FadeTransition(
            opacity: curve,
            child: SlideTransition(
              position: Tween<Offset>(begin: begin, end: end).animate(curve),
              child: child,
            ),
          );
        },
        transitionDuration: const Duration(milliseconds: 320),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final candidates = _filteredCandidates;
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 900;
    final paddingH = isCompact ? 20.0 : 44.0;

    return Scaffold(
      backgroundColor: AppColors.canvas,
      body: Stack(
        children: [
          // Background subtle registration crosshairs
          Positioned(
            left: 20,
            top: 180,
            child: IgnorePointer(
              child: const RegistrationCross(size: 18),
            ),
          ),
          Positioned(
            right: 20,
            top: 180,
            child: IgnorePointer(
              child: const RegistrationCross(size: 18),
            ),
          ),

          // Main Viewport Column (No Primary Vertical Scrolling)
          Padding(
            padding: const EdgeInsets.only(top: 76),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Compact Editorial Header Block
                Padding(
                  padding: EdgeInsets.fromLTRB(paddingH, 20, paddingH, 12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                'INDEX / 2026',
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 1.5,
                                  color: AppColors.textMuted,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Text(
                                '//  HORIZONTAL CAROUSEL',
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w500,
                                  letterSpacing: 1.2,
                                  color: AppColors.emerald,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'RESUME DOSSIER COLLECTION',
                            style: GoogleFonts.syne(
                              fontSize: isCompact ? 24 : 36,
                              fontWeight: FontWeight.w800,
                              letterSpacing: -1.0,
                              color: AppColors.textWhite,
                            ),
                          ),
                        ],
                      ),

                      // Reset Filters cue
                      if (_selectedCategory != 'ALL' || _searchQuery.isNotEmpty)
                        MouseRegion(
                          cursor: SystemMouseCursors.click,
                          child: GestureDetector(
                            onTap: () {
                              setState(() {
                                _selectedCategory = 'ALL';
                                _searchQuery = '';
                              });
                            },
                            child: Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                              child: Text(
                                '[RESET FILTERS]',
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.8,
                                  color: AppColors.emerald,
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),

                // Hairline Divider
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: paddingH),
                  child: Container(
                    height: 0.8,
                    color: AppColors.hairlineSubtle,
                  ),
                ),

                const SizedBox(height: 10),

                // Primary Horizontal Carousel Area or Empty State
                Expanded(
                  child: candidates.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const RegistrationCross(size: 24),
                              const SizedBox(height: 20),
                              Text(
                                'NO DOSSIERS MATCH SELECTION',
                                style: GoogleFonts.syne(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.textWhite,
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                'Try resetting filters or adjusting search parameters.',
                                style: GoogleFonts.spaceGrotesk(
                                  fontSize: 13,
                                  color: AppColors.textMuted,
                                ),
                              ),
                              const SizedBox(height: 20),
                              MouseRegion(
                                cursor: SystemMouseCursors.click,
                                child: GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      _selectedCategory = 'ALL';
                                      _searchQuery = '';
                                    });
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 16,
                                      vertical: 8,
                                    ),
                                    decoration: BoxDecoration(
                                      border: Border.all(
                                        color: AppColors.hairlineActive,
                                        width: 0.8,
                                      ),
                                    ),
                                    child: Text(
                                      'RESET ALL FILTERS',
                                      style: GoogleFonts.jetBrainsMono(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 1.0,
                                        color: AppColors.textWhite,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        )
                      : HorizontalResumeCarousel(
                          key: ValueKey('carousel_${_selectedCategory}_$_sortBy'),
                          candidates: candidates,
                          onSelectCandidate: (candidate) =>
                              _openCandidateDetail(candidate, candidates),
                        ),
                ),

                // Bottom Archival Colophon Bar
                Container(
                  padding: EdgeInsets.symmetric(
                    horizontal: paddingH,
                    vertical: 14,
                  ),
                  decoration: const BoxDecoration(
                    color: AppColors.canvas,
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
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'NEXORA',
                            style: GoogleFonts.syne(
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 2.0,
                              color: AppColors.textWhite,
                            ),
                          ),
                          Text(
                            ' // HORIZONTAL COLLECTION ARCHIVE',
                            style: GoogleFonts.jetBrainsMono(
                              fontSize: 10.5,
                              fontWeight: FontWeight.w500,
                              letterSpacing: 1.2,
                              color: AppColors.textMuted,
                            ),
                          ),
                        ],
                      ),
                      Text(
                        '${candidates.length} OF ${dummyCandidates.length} DOSSIERS LOADED',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1.0,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Preserved Fixed Top Camille Mormal Navigation Bar
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: CamilleNavBar(
              totalCount: dummyCandidates.length,
              peakMatch: 97,
              selectedCategory: _selectedCategory,
              onCategorySelected: (cat) => setState(() => _selectedCategory = cat),
              sortBy: _sortBy,
              onSortChanged: (sort) => setState(() => _sortBy = sort),
              searchQuery: _searchQuery,
              onSearchChanged: (q) => setState(() => _searchQuery = q),
              categories: _categories,
            ),
          ),
        ],
      ),
    );
  }
}
