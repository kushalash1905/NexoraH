import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class CamilleNavBar extends StatefulWidget {
  final int totalCount;
  final int peakMatch;
  final String selectedCategory;
  final ValueChanged<String> onCategorySelected;
  final String sortBy;
  final ValueChanged<String> onSortChanged;
  final String searchQuery;
  final ValueChanged<String> onSearchChanged;
  final List<String> categories;

  const CamilleNavBar({
    super.key,
    required this.totalCount,
    required this.peakMatch,
    required this.selectedCategory,
    required this.onCategorySelected,
    required this.sortBy,
    required this.onSortChanged,
    required this.searchQuery,
    required this.onSearchChanged,
    required this.categories,
  });

  @override
  State<CamilleNavBar> createState() => _CamilleNavBarState();
}

class _CamilleNavBarState extends State<CamilleNavBar> {
  bool _searchOpen = false;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _searchController.text = widget.searchQuery;
  }

  @override
  void didUpdateWidget(covariant CamilleNavBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.searchQuery != _searchController.text) {
      _searchController.text = widget.searchQuery;
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 960;

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 24 : 44,
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
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Row 1: Brandmark, Center Filter Links, Right Metadata & Search
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Left: Brandmark in Camille Mormal typography
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'NEXORA',
                    style: GoogleFonts.syne(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 2.5,
                      color: AppColors.textWhite,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '// ARCHIVE',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      letterSpacing: 1.2,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),

              // Center: Unboxed Minimalist Category Links (hidden on compact screens)
              if (!isCompact)
                Expanded(
                  child: Center(
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: widget.categories.map((category) {
                          final isSelected = widget.selectedCategory == category;
                          return _NavCategoryLink(
                            label: _formatCategoryLabel(category),
                            isSelected: isSelected,
                            onTap: () => widget.onCategorySelected(category),
                          );
                        }).toList(),
                      ),
                    ),
                  ),
                ),

              // Right: Controls (Search Trigger, Sort Toggle, Dossier Count)
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Search Toggle
                  MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: () => setState(() => _searchOpen = !_searchOpen),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: _searchOpen
                              ? AppColors.plateElevated
                              : Colors.transparent,
                          border: Border.all(
                            color: _searchOpen
                                ? AppColors.hairlineActive
                                : AppColors.hairline,
                            width: 0.8,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.search,
                              size: 13,
                              color: AppColors.textWhite,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              _searchOpen ? 'CLOSE' : 'SEARCH',
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.8,
                                color: AppColors.textWhite,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 12),

                  // Sort Dropdown / Selector
                  Container(
                    height: 27,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    decoration: BoxDecoration(
                      border: Border.all(color: AppColors.hairline, width: 0.8),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: widget.sortBy,
                        dropdownColor: AppColors.plateElevated,
                        icon: const Icon(
                          Icons.keyboard_arrow_down,
                          size: 13,
                          color: AppColors.textMuted,
                        ),
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 0.6,
                          color: AppColors.textWhite,
                        ),
                        items: const [
                          DropdownMenuItem(
                            value: 'score',
                            child: Text('SORT: SCORE'),
                          ),
                          DropdownMenuItem(
                            value: 'exp',
                            child: Text('SORT: EXPERIENCE'),
                          ),
                          DropdownMenuItem(
                            value: 'index',
                            child: Text('SORT: INDEX'),
                          ),
                        ],
                        onChanged: (val) {
                          if (val != null) widget.onSortChanged(val);
                        },
                      ),
                    ),
                  ),

                  const SizedBox(width: 14),

                  // Archival Index Ticker
                  Text(
                    '${widget.totalCount.toString().padLeft(2, '0')} DOSSIERS',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 10.5,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1.0,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ],
          ),

          // Compact View Category Scroll Bar
          if (isCompact) ...[
            const SizedBox(height: 14),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: widget.categories.map((category) {
                  final isSelected = widget.selectedCategory == category;
                  return _NavCategoryLink(
                    label: _formatCategoryLabel(category),
                    isSelected: isSelected,
                    onTap: () => widget.onCategorySelected(category),
                  );
                }).toList(),
              ),
            ),
          ],

          // Expandable Minimalist Search Bar
          if (_searchOpen) ...[
            const SizedBox(height: 14),
            Container(
              height: 38,
              padding: const EdgeInsets.symmetric(horizontal: 14),
              decoration: BoxDecoration(
                color: AppColors.plate,
                border: Border.all(color: AppColors.hairlineActive, width: 0.8),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.search,
                    size: 14,
                    color: AppColors.textMuted,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      autofocus: true,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 13,
                        color: AppColors.textWhite,
                      ),
                      cursorColor: AppColors.emerald,
                      decoration: InputDecoration(
                        hintText: 'Filter by name, skills, category, or keyword...',
                        hintStyle: GoogleFonts.spaceGrotesk(
                          fontSize: 13,
                          color: AppColors.textMuted,
                        ),
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: EdgeInsets.zero,
                      ),
                      onChanged: widget.onSearchChanged,
                    ),
                  ),
                  if (_searchController.text.isNotEmpty)
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () {
                          _searchController.clear();
                          widget.onSearchChanged('');
                        },
                        child: const Icon(
                          Icons.close,
                          size: 14,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatCategoryLabel(String cat) {
    if (cat == 'ALL') return 'ALL';
    if (cat == 'Systems & Distributed') return 'SYSTEMS';
    if (cat == 'AI & Machine Learning') return 'AI / ML';
    if (cat == 'Creative & Frontend') return 'CREATIVE';
    if (cat == 'Cloud & Infrastructure') return 'CLOUD';
    if (cat == 'Full-Stack & Web') return 'FULL-STACK';
    if (cat == 'Mobile & Flutter') return 'MOBILE';
    if (cat == 'Security & Cloud') return 'SECURITY';
    return cat.toUpperCase();
  }
}

class _NavCategoryLink extends StatefulWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavCategoryLink({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  State<_NavCategoryLink> createState() => _NavCategoryLinkState();
}

class _NavCategoryLinkState extends State<_NavCategoryLink> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final active = widget.isSelected || _isHovered;

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (widget.isSelected) ...[
                Container(
                  width: 4,
                  height: 4,
                  decoration: const BoxDecoration(
                    color: AppColors.emerald,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
              ],
              Text(
                widget.label,
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 11,
                  fontWeight: widget.isSelected ? FontWeight.w700 : FontWeight.w500,
                  letterSpacing: 1.0,
                  color: active
                      ? AppColors.textWhite
                      : AppColors.textDim,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
