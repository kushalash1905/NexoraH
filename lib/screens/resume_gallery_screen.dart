import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../data/dummy_candidates.dart';
import '../models/candidate.dart';
import '../services/resume_upload_service.dart';
import '../theme/app_theme.dart';
import '../widgets/camille_nav_bar.dart';
import '../widgets/horizontal_resume_carousel.dart';
import '../widgets/ranking_podium_view.dart';
import '../widgets/recruitr_hero_section.dart';
import '../widgets/registration_cross.dart';
import 'resume_detail_screen.dart';

class ResumeGalleryScreen extends StatefulWidget {
  const ResumeGalleryScreen({super.key});

  @override
  State<ResumeGalleryScreen> createState() => _ResumeGalleryScreenState();
}

class _ResumeGalleryScreenState extends State<ResumeGalleryScreen> {
  final List<Candidate> _demoCandidates = List.from(dummyCandidates);
  final List<Candidate> _uploadedCandidates = [];

  String _selectedCategory = 'ALL';
  String _sortBy = 'score'; // 'score', 'exp', 'index'
  String _searchQuery = '';
  bool _showRankingView = false;
  bool _isUploading = false;
  String? _uploadSuccessMessage;

  late final ScrollController _scrollController;
  double _scrollProgress = 0.0;
  bool _isCarouselHovered = false;
  int _activeCarouselPointers = 0;

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

  /// Active candidate pool:
  /// Before any upload: returns demo candidates.
  /// After the first upload: returns ONLY user-uploaded candidates.
  List<Candidate> get _allCandidates =>
      _uploadedCandidates.isNotEmpty ? _uploadedCandidates : _demoCandidates;

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (!_scrollController.hasClients) return;
    final screenHeight = MediaQuery.of(context).size.height;
    if (screenHeight <= 0) return;
    final progress = (_scrollController.offset / screenHeight).clamp(0.0, 1.0);
    if ((progress - _scrollProgress).abs() > 0.01) {
      setState(() => _scrollProgress = progress);
    }
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  List<Candidate> get _filteredCandidates {
    var list = _allCandidates.where((c) {
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

  Future<void> _handleUploadResumes() async {
    setState(() => _isUploading = true);
    try {
      final existingNames = _uploadedCandidates.map((c) => c.name.toLowerCase()).toSet();
      final newCandidates = await ResumeUploadService.pickAndCreateCandidates(
        currentTotalCount: _uploadedCandidates.length,
        defaultCategory: _selectedCategory != 'ALL' ? _selectedCategory : 'Full-Stack & Web',
        existingNames: existingNames,
      );

      if (newCandidates.isNotEmpty && mounted) {
        setState(() {
          _uploadedCandidates.addAll(newCandidates);
          _uploadSuccessMessage =
              '${newCandidates.length} DOSSIER${newCandidates.length > 1 ? 'S' : ''} INDEXED INTO CAROUSEL';
        });

        Future.delayed(const Duration(seconds: 4), () {
          if (mounted && _uploadSuccessMessage != null) {
            setState(() => _uploadSuccessMessage = null);
          }
        });
      }
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
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
    final screenSize = MediaQuery.of(context).size;
    final screenWidth = screenSize.width;
    final screenHeight = screenSize.height;
    final isCompact = screenWidth < 960;
    final paddingH = isCompact ? 20.0 : 44.0;

    return Scaffold(
      backgroundColor: AppColors.canvas,
      body: Stack(
        children: [
          // Vertical smooth scroll container: Section 1 (Hero) and Section 2 (Existing Archive UI)
          SingleChildScrollView(
            controller: _scrollController,
            physics: (_isCarouselHovered || _activeCarouselPointers > 0)
                ? const NeverScrollableScrollPhysics()
                : const ClampingScrollPhysics(),
            child: Column(
              children: [
                // SECTION 1: New Dramatic RecruitR Landing Hero
                RecruitRHeroSection(
                  scrollProgress: _scrollProgress,
                  onExploreTap: () {
                    _scrollController.animateTo(
                      screenHeight,
                      duration: const Duration(milliseconds: 700),
                      curve: Curves.easeInOutCubic,
                    );
                  },
                ),

                // SECTION 2: Locked Existing Archive UI (exactly height = screenHeight)
                SizedBox(
                  height: screenHeight,
                  child: Stack(
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

                      // Main Viewport Column
                      Padding(
                        padding: const EdgeInsets.only(top: 76),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Compact Editorial Header Block
                            Padding(
                              padding: EdgeInsets.fromLTRB(paddingH, 18, paddingH, 10),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  // Left: Section Identity
                                  Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'RESUME DOSSIER COLLECTION',
                                        style: GoogleFonts.syne(
                                          fontSize: isCompact ? 22 : 32,
                                          fontWeight: FontWeight.w800,
                                          letterSpacing: -1.0,
                                          color: AppColors.textWhite,
                                        ),
                                      ),
                                    ],
                                  ),

                                  // Right: Editorial Action Buttons (Upload & Rank)
                                  Flexible(
                                    child: _buildHeaderActions(),
                                  ),
                                ],
                              ),
                            ),

                            // Upload Feedback Banner (if active)
                            if (_uploadSuccessMessage != null)
                              Padding(
                                padding: EdgeInsets.fromLTRB(paddingH, 0, paddingH, 8),
                                child: Row(
                                  children: [
                                    Container(
                                      width: 6,
                                      height: 6,
                                      decoration: const BoxDecoration(
                                        color: AppColors.emerald,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      '// $_uploadSuccessMessage',
                                      style: GoogleFonts.jetBrainsMono(
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.w600,
                                        letterSpacing: 1.0,
                                        color: AppColors.emerald,
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

                            const SizedBox(height: 8),

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
                                            'Try resetting filters or uploading new resumes.',
                                            style: GoogleFonts.spaceGrotesk(
                                              fontSize: 13,
                                              color: AppColors.textMuted,
                                            ),
                                          ),
                                          const SizedBox(height: 20),
                                          Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
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
                                              const SizedBox(width: 12),
                                              MouseRegion(
                                                cursor: SystemMouseCursors.click,
                                                child: GestureDetector(
                                                  onTap: _handleUploadResumes,
                                                  child: Container(
                                                    padding: const EdgeInsets.symmetric(
                                                      horizontal: 16,
                                                      vertical: 8,
                                                    ),
                                                    decoration: BoxDecoration(
                                                      color: AppColors.plate,
                                                      border: Border.all(
                                                        color: AppColors.emerald,
                                                        width: 0.8,
                                                      ),
                                                    ),
                                                    child: Text(
                                                      'UPLOAD RESUMES',
                                                      style: GoogleFonts.jetBrainsMono(
                                                        fontSize: 11,
                                                        fontWeight: FontWeight.w700,
                                                        letterSpacing: 1.0,
                                                        color: AppColors.emerald,
                                                      ),
                                                    ),
                                                  ),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),
                                    )
                                  : MouseRegion(
                                      onEnter: (_) => setState(() => _isCarouselHovered = true),
                                      onExit: (_) {
                                        if (mounted) {
                                          setState(() => _isCarouselHovered = false);
                                        }
                                      },
                                      child: Listener(
                                        onPointerDown: (_) {
                                          _activeCarouselPointers++;
                                          if (!_isCarouselHovered && mounted) {
                                            setState(() => _isCarouselHovered = true);
                                          }
                                        },
                                        onPointerUp: (_) {
                                          if (_activeCarouselPointers > 0) _activeCarouselPointers--;
                                        },
                                        onPointerCancel: (_) {
                                          if (_activeCarouselPointers > 0) _activeCarouselPointers--;
                                        },
                                        child: HorizontalResumeCarousel(
                                          key: ValueKey(
                                            'carousel_${_selectedCategory}_${_sortBy}_${candidates.length}',
                                          ),
                                          candidates: candidates,
                                          onSelectCandidate: (candidate) =>
                                              _openCandidateDetail(candidate, candidates),
                                        ),
                                      ),
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
                                  Text(
                                    'RECRUITR',
                                    style: GoogleFonts.syne(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: 2.0,
                                      color: AppColors.textWhite,
                                    ),
                                  ),
                                  Text(
                                    '${candidates.length} OF ${_allCandidates.length} DOSSIERS LOADED',
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

                      // Preserved Top Camille Mormal Navigation Bar
                      Positioned(
                        top: 0,
                        left: 0,
                        right: 0,
                        child: CamilleNavBar(
                          totalCount: _allCandidates.length,
                          peakMatch: _allCandidates.isNotEmpty
                              ? _allCandidates
                                  .map((c) => c.matchScore)
                                  .reduce((a, b) => a > b ? a : b)
                              : 97,
                          selectedCategory: _selectedCategory,
                          onCategorySelected: (cat) => setState(() => _selectedCategory = cat),
                          sortBy: _sortBy,
                          onSortChanged: (sort) => setState(() => _sortBy = sort),
                          searchQuery: _searchQuery,
                          onSearchChanged: (q) => setState(() => _searchQuery = q),
                          categories: _categories,
                          onBrandmarkTap: () {
                            _scrollController.animateTo(
                              0.0,
                              duration: const Duration(milliseconds: 700),
                              curve: Curves.easeInOutCubic,
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Candidate Ranking Podium Overlay
          if (_showRankingView)
            Positioned.fill(
              child: RankingPodiumView(
                candidates: _allCandidates,
                onSelectCandidate: (candidate) =>
                    _openCandidateDetail(candidate, _allCandidates),
                onClose: () => setState(() => _showRankingView = false),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildHeaderActions() {
    return Wrap(
      alignment: WrapAlignment.end,
      spacing: 10,
      runSpacing: 8,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
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
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 6),
                child: Text(
                  '[RESET FILTERS]',
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 10.5,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.8,
                    color: AppColors.emerald,
                  ),
                ),
              ),
            ),
          ),

        // Multiple Resume Upload Button
        MouseRegion(
          cursor: SystemMouseCursors.click,
          child: GestureDetector(
            onTap: _isUploading ? null : _handleUploadResumes,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
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
                  Icon(
                    _isUploading ? Icons.hourglass_top : Icons.upload_file,
                    size: 13,
                    color: AppColors.emerald,
                  ),
                  const SizedBox(width: 7),
                  Text(
                    _isUploading ? 'INDEXING...' : 'UPLOAD RESUMES',
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

        // Rank Candidates Button
        MouseRegion(
          cursor: SystemMouseCursors.click,
          child: GestureDetector(
            onTap: () => setState(() => _showRankingView = true),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
              decoration: BoxDecoration(
                color: AppColors.plate,
                border: Border.all(
                  color: AppColors.emerald.withValues(alpha: 0.7),
                  width: 0.8,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.emerald.withValues(alpha: 0.08),
                    blurRadius: 14,
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.leaderboard_outlined,
                    size: 13,
                    color: AppColors.emerald,
                  ),
                  const SizedBox(width: 7),
                  Text(
                    'RANK CANDIDATES',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 10.5,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.8,
                      color: AppColors.emerald,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
