import 'dart:math' as math;
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/candidate.dart';
import '../theme/app_theme.dart';
import 'carousel_resume_card.dart';

typedef OnCandidateSelected = void Function(Candidate candidate);

class HorizontalResumeCarousel extends StatefulWidget {
  final List<Candidate> candidates;
  final OnCandidateSelected onSelectCandidate;

  const HorizontalResumeCarousel({
    super.key,
    required this.candidates,
    required this.onSelectCandidate,
  });

  @override
  State<HorizontalResumeCarousel> createState() =>
      _HorizontalResumeCarouselState();
}

class _HorizontalResumeCarouselState extends State<HorizontalResumeCarousel> {
  late PageController _pageController;
  int _currentPage = 0;
  double _currentFraction = 0.32;
  double _lastScreenWidth = 0;
  DateTime _lastScrollTime = DateTime.now();

  @override
  void initState() {
    super.initState();
    _pageController = PageController(
      initialPage: _currentPage,
      viewportFraction: _currentFraction,
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _updateFractionIfNeeded();
  }

  void _updateFractionIfNeeded() {
    final screenWidth = MediaQuery.of(context).size.width;
    if ((screenWidth - _lastScreenWidth).abs() < 8 && _lastScreenWidth > 0) {
      return;
    }
    _lastScreenWidth = screenWidth;
    final newFraction = _calculateViewportFraction(screenWidth);
    if ((newFraction - _currentFraction).abs() > 0.02) {
      final oldPage = _pageController.hasClients && _pageController.page != null
          ? _pageController.page!.round()
          : _currentPage;
      _currentFraction = newFraction;
      final oldController = _pageController;
      _pageController = PageController(
        initialPage: oldPage.clamp(0, math.max(0, widget.candidates.length - 1)),
        viewportFraction: _currentFraction,
      );
      WidgetsBinding.instance.addPostFrameCallback((_) {
        oldController.dispose();
      });
      if (mounted) setState(() {});
    }
  }

  @override
  void didUpdateWidget(covariant HorizontalResumeCarousel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.candidates.length != oldWidget.candidates.length) {
      if (_currentPage >= widget.candidates.length && widget.candidates.isNotEmpty) {
        _currentPage = widget.candidates.length - 1;
      }
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _goToPrevious() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
      );
    }
  }

  void _goToNext() {
    if (_currentPage < widget.candidates.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
      );
    }
  }

  void _onPointerScroll(PointerScrollEvent event) {
    if (!_pageController.hasClients) return;

    final now = DateTime.now();
    if (now.difference(_lastScrollTime).inMilliseconds < 350) {
      return;
    }

    final delta = event.scrollDelta.dx != 0
        ? event.scrollDelta.dx
        : event.scrollDelta.dy;

    if (delta.abs() > 15) {
      _lastScrollTime = now;
      if (delta > 0) {
        _goToNext();
      } else {
        _goToPrevious();
      }
    }
  }

  double _getCardWidth(double screenWidth) {
    if (screenWidth >= 1600) {
      return 430.0;
    } else if (screenWidth >= 1200) {
      return 410.0;
    } else if (screenWidth >= 800) {
      return 380.0;
    } else {
      return (screenWidth * 0.80).clamp(280.0, 380.0);
    }
  }

  double _getCardHeight(double screenHeight) {
    if (screenHeight < 720) {
      return 410.0;
    }
    return 440.0;
  }

  double _calculateViewportFraction(double screenWidth) {
    final cardWidth = _getCardWidth(screenWidth);
    const spacing = 24.0;
    final step = cardWidth + spacing;
    return (step / screenWidth).clamp(0.20, 0.86);
  }

  @override
  Widget build(BuildContext context) {
    final candidates = widget.candidates;
    if (candidates.isEmpty) {
      return const SizedBox.shrink();
    }

    final screenSize = MediaQuery.of(context).size;
    final screenWidth = screenSize.width;
    final screenHeight = screenSize.height;
    final cardWidth = _getCardWidth(screenWidth);
    final cardHeight = _getCardHeight(screenHeight);

    return Focus(
      autofocus: true,
      onKeyEvent: (node, event) {
        if (event is KeyDownEvent) {
          if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
            _goToPrevious();
            return KeyEventResult.handled;
          } else if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
            _goToNext();
            return KeyEventResult.handled;
          }
        }
        return KeyEventResult.ignored;
      },
      child: Column(
        children: [
          // The Horizontal Snapping Carousel
          Expanded(
            child: Listener(
              onPointerSignal: (pointerSignal) {
                if (pointerSignal is PointerScrollEvent) {
                  _onPointerScroll(pointerSignal);
                }
              },
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // PageView Builder with Smooth Snapping and Center Focus
                  PageView.builder(
                    controller: _pageController,
                    itemCount: candidates.length,
                    pageSnapping: true,
                    clipBehavior: Clip.none,
                    onPageChanged: (page) {
                      setState(() => _currentPage = page);
                    },
                    itemBuilder: (context, index) {
                      final candidate = candidates[index];

                      return AnimatedBuilder(
                        animation: _pageController,
                        builder: (context, child) {
                          double page = _currentPage.toDouble();
                          if (_pageController.hasClients &&
                              _pageController.position.haveDimensions &&
                              _pageController.page != null) {
                            page = _pageController.page!;
                          }

                          // Distance from active center
                          final diff = (index - page).abs();

                          // focusFactor: 1.0 at dead center, decays to 0.0 for neighbors
                          final focusFactor = (1.0 - diff).clamp(0.0, 1.0);

                          // Smooth continuous scale interpolation:
                          // Center (diff = 0) -> scale ≈ 1.0
                          // Neighbors (diff = 1) -> scale ≈ 0.91 (within 0.88-0.94 range)
                          // Further cards (diff >= 2) -> scale ≈ 0.82 (within 0.80-0.88 range)
                          final scale = (1.0 - (diff.clamp(0.0, 2.0) * 0.09)).clamp(0.82, 1.0);

                          // Smooth continuous opacity interpolation:
                          // Center -> 1.0, Neighbors -> ~0.76, Further -> ~0.44
                          final opacity = (1.0 - (diff.clamp(0.0, 2.0) * 0.28)).clamp(0.44, 1.0);

                          final isCenter = diff < 0.5;

                          return Center(
                            child: Transform.scale(
                              scale: scale,
                              child: Opacity(
                                opacity: opacity,
                                child: CarouselResumeCard(
                                  candidate: candidate,
                                  isFocused: isCenter,
                                  focusFactor: focusFactor,
                                  cardWidth: cardWidth,
                                  cardHeight: cardHeight,
                                  onTap: () {
                                    if (!isCenter) {
                                      // Animate tapped neighbor card to center
                                      _pageController.animateToPage(
                                        index,
                                        duration: const Duration(milliseconds: 320),
                                        curve: Curves.easeOutCubic,
                                      );
                                    } else {
                                      // Open dossier detail screen
                                      widget.onSelectCandidate(candidate);
                                    }
                                  },
                                  onOpenDetail: () {
                                    widget.onSelectCandidate(candidate);
                                  },
                                ),
                              ),
                            ),
                          );
                        },
                      );
                    },
                  ),

                  // Floating Navigation Chevrons on Left & Right
                  Positioned(
                    left: 20,
                    child: _CarouselArrowButton(
                      icon: Icons.chevron_left,
                      isEnabled: _currentPage > 0,
                      onTap: _goToPrevious,
                    ),
                  ),
                  Positioned(
                    right: 20,
                    child: _CarouselArrowButton(
                      icon: Icons.chevron_right,
                      isEnabled: _currentPage < candidates.length - 1,
                      onTap: _goToNext,
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Bottom Progress & Stepper Bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Left: Active Candidate Index
                Row(
                  children: [
                    Text(
                      (_currentPage + 1).toString().padLeft(2, '0'),
                      style: GoogleFonts.syne(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: AppColors.textWhite,
                      ),
                    ),
                    Text(
                      ' / ${candidates.length.toString().padLeft(2, '0')} DOSSIERS',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.0,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),

                // Center: Minimalist Stepper Dots / Bars
                if (candidates.length <= 18)
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: List.generate(candidates.length, (idx) {
                      final isCurrent = idx == _currentPage;
                      return MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap: () => _pageController.animateToPage(
                            idx,
                            duration: const Duration(milliseconds: 320),
                            curve: Curves.easeOutCubic,
                          ),
                          child: Container(
                            margin: const EdgeInsets.symmetric(horizontal: 2.5),
                            width: isCurrent ? 24 : 10,
                            height: 2.5,
                            decoration: BoxDecoration(
                              color: isCurrent
                                  ? AppColors.emerald
                                  : AppColors.hairlineActive,
                              borderRadius: BorderRadius.circular(1),
                            ),
                          ),
                        ),
                      );
                    }),
                  ),

                // Right: Interaction Hint
                Row(
                  children: [
                    Text(
                      'DRAG OR USE [← →] TO EXPLORE',
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 10,
                        fontWeight: FontWeight.w500,
                        letterSpacing: 1.0,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CarouselArrowButton extends StatelessWidget {
  final IconData icon;
  final bool isEnabled;
  final VoidCallback onTap;

  const _CarouselArrowButton({
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
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: AppColors.plate.withValues(alpha: 0.85),
            border: Border.all(
              color: isEnabled ? AppColors.hairlineActive : AppColors.hairlineSubtle,
              width: 0.8,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.4),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Icon(
            icon,
            size: 22,
            color: isEnabled ? AppColors.textWhite : AppColors.textDim,
          ),
        ),
      ),
    );
  }
}
