import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class EditorialHeader extends StatelessWidget {
  final int totalCount;
  final int matchAverage;
  final int topScore;
  final String selectedCategory;
  final ValueChanged<String> onCategorySelected;
  final String sortBy;
  final ValueChanged<String> onSortChanged;
  final String searchQuery;
  final ValueChanged<String> onSearchChanged;
  final List<String> categories;

  const EditorialHeader({
    super.key,
    required this.totalCount,
    required this.matchAverage,
    required this.topScore,
    required this.selectedCategory,
    required this.onCategorySelected,
    required this.sortBy,
    required this.onSortChanged,
    required this.searchQuery,
    required this.onSearchChanged,
    required this.categories,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 900;

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 20 : 48,
        vertical: isCompact ? 24 : 36,
      ),
      decoration: const BoxDecoration(
        color: AppColors.canvas,
        border: Border(
          bottom: BorderSide(
            color: AppColors.borderSubtle,
            width: 1.0,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top Bar: Brand, Status, and Metrics
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Brand Monogram & Title
              Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      color: AppColors.emerald,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'NEXORA',
                    style: GoogleFonts.syne(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 2.0,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  Text(
                    ' / ARCHIVE',
                    style: GoogleFonts.syne(
                      fontSize: 16,
                      fontWeight: FontWeight.w400,
                      letterSpacing: 2.0,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),

              // Live Status / Metadata
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(2),
                      border: Border.all(color: AppColors.borderSubtle, width: 0.8),
                    ),
                    child: Row(
                      children: [
                        Text(
                          'INDEX NO. 2026 // HACKATHON STAGE',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 0.8,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),

          SizedBox(height: isCompact ? 24 : 36),

          // Main Editorial Title & Headline
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'RESUME DOSSIER COLLECTION',
                      style: GoogleFonts.syne(
                        fontSize: isCompact ? 30 : 44,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -1.2,
                        height: 1.05,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'A curated index of 18 candidate profiles evaluated against target requirements.',
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: isCompact ? 13 : 15,
                        fontWeight: FontWeight.w400,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),

              // Minimalist Stats Counters (hidden on very small viewports)
              if (!isCompact)
                Row(
                  children: [
                    _StatBlock(
                      label: 'TOTAL DOSSIERS',
                      value: '$totalCount',
                    ),
                    const SizedBox(width: 24),
                    _StatBlock(
                      label: 'PEAK MATCH',
                      value: '$topScore%',
                      highlight: true,
                    ),
                    const SizedBox(width: 24),
                    _StatBlock(
                      label: 'AVG MATCH',
                      value: '$matchAverage%',
                    ),
                  ],
                ),
            ],
          ),

          SizedBox(height: isCompact ? 24 : 32),

          // Controls Bar: Category Chips, Search, and Sort
          Wrap(
            spacing: 12,
            runSpacing: 14,
            alignment: WrapAlignment.spaceBetween,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              // Category Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: categories.map((cat) {
                    final isSelected = selectedCategory == cat;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap: () => onCategorySelected(cat),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 180),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 7,
                            ),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? AppColors.textPrimary
                                  : AppColors.surface,
                              borderRadius: BorderRadius.circular(2),
                              border: Border.all(
                                color: isSelected
                                    ? AppColors.textPrimary
                                    : AppColors.border,
                                width: 0.8,
                              ),
                            ),
                            child: Text(
                              cat.toUpperCase(),
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 11,
                                fontWeight: isSelected
                                    ? FontWeight.w700
                                    : FontWeight.w500,
                                letterSpacing: 0.6,
                                color: isSelected
                                    ? AppColors.canvas
                                    : AppColors.textSecondary,
                              ),
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),

              // Search Box & Sort Selector
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Search Box
                  Container(
                    width: isCompact ? 160 : 210,
                    height: 34,
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(2),
                      border: Border.all(color: AppColors.border, width: 0.8),
                    ),
                    child: TextField(
                      onChanged: onSearchChanged,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 12,
                        color: AppColors.textPrimary,
                      ),
                      cursorColor: AppColors.emerald,
                      decoration: InputDecoration(
                        hintText: 'Filter candidates...',
                        hintStyle: GoogleFonts.spaceGrotesk(
                          fontSize: 12,
                          color: AppColors.textMuted,
                        ),
                        prefixIcon: const Icon(
                          Icons.search,
                          size: 14,
                          color: AppColors.textMuted,
                        ),
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 9,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 10),

                  // Sort Selector Dropdown
                  Container(
                    height: 34,
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(2),
                      border: Border.all(color: AppColors.border, width: 0.8),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: sortBy,
                        dropdownColor: AppColors.surfaceElevated,
                        icon: const Icon(
                          Icons.keyboard_arrow_down_rounded,
                          size: 16,
                          color: AppColors.textMuted,
                        ),
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textSecondary,
                        ),
                        items: const [
                          DropdownMenuItem(
                            value: 'score',
                            child: Text('SORT: HIGHEST SCORE'),
                          ),
                          DropdownMenuItem(
                            value: 'exp',
                            child: Text('SORT: EXPERIENCE'),
                          ),
                          DropdownMenuItem(
                            value: 'index',
                            child: Text('SORT: INDEX NUMBER'),
                          ),
                        ],
                        onChanged: (val) {
                          if (val != null) onSortChanged(val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatBlock extends StatelessWidget {
  final String label;
  final String value;
  final bool highlight;

  const _StatBlock({
    required this.label,
    required this.value,
    this.highlight = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(2),
        border: Border.all(
          color: highlight
              ? AppColors.emerald.withValues(alpha: 0.3)
              : AppColors.borderSubtle,
          width: 0.8,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.jetBrainsMono(
              fontSize: 9.5,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.8,
              color: AppColors.textMuted,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: GoogleFonts.jetBrainsMono(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: highlight ? AppColors.emerald : AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
