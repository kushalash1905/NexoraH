import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppColors {
  // Exact Camille Mormal Matte Background
  static const Color canvas = Color(0xFF141414);
  static const Color canvasSubtle = Color(0xFF181818);
  
  // Artifact Plates & Surfaces
  static const Color plate = Color(0xFF1C1C1C);
  static const Color plateElevated = Color(0xFF222222);
  static const Color plateHover = Color(0xFF282828);

  // Surface aliases for backward compatibility
  static const Color surface = Color(0xFF1C1C1C);
  static const Color surfaceElevated = Color(0xFF222222);
  static const Color surfaceHover = Color(0xFF282828);

  // Hairline Rules & Dividers
  static const Color hairline = Color(0x1FFFFFFF); // 12% white
  static const Color hairlineSubtle = Color(0x0EFFFFFF); // 5% white
  static const Color hairlineActive = Color(0x4DFFFFFF); // 30% white
  static const Color crosshair = Color(0x33FFFFFF); // 20% white

  // Border aliases
  static const Color border = Color(0x1FFFFFFF);
  static const Color borderSubtle = Color(0x0EFFFFFF);
  static const Color borderActive = Color(0x4DFFFFFF);

  // Authentic Paper Document Tones
  static const Color paper = Color(0xFFFAF9F5);
  static const Color paperSurface = Color(0xFFF3F1EA);
  static const Color paperBorder = Color(0xFFE4E0D5);
  static const Color inkPrimary = Color(0xFF111111);
  static const Color inkSecondary = Color(0xFF333744);
  static const Color inkMuted = Color(0xFF5A6072);
  static const Color inkDivider = Color(0xFFDDD9CD);

  // Camille Mormal Typography Colors (Enhanced Legibility & Subtle Contrast Polish)
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xD9FFFFFF); // 85% white
  static const Color textMuted = Color(0xFFB4B7C4); // Refined high-legibility slate gray (6.5:1 contrast)
  static const Color textDim = Color(0x99FFFFFF); // 60% white for crisp metadata
  static const Color textFaint = Color(0x4DFFFFFF); // 30% white

  // Performance Metric — Vibrant, tasteful, energetic lime green exclusively for positive scores
  static const Color limeScore = Color(0xFF96E032);
  static const Color limeScoreMuted = Color(0x3396E032);

  // Brand & UI Accents — Cozy, sophisticated editorial pastel pink
  static const Color pastelPink = Color(0xFFF0A8BA);
  static const Color pastelPinkFaint = Color(0x26F0A8BA);
  static const Color pastelPinkBorder = Color(0x66F0A8BA);

  // Map emerald aliases to cozy pastel pink for all decorative and UI elements
  static const Color emerald = pastelPink;
  static const Color emeraldFaint = pastelPinkFaint;
  static const Color cyanAccent = Color(0xFF38BDF8);
}

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.canvas,
      colorScheme: const ColorScheme.dark(
        surface: AppColors.plate,
        primary: AppColors.pastelPink,
        secondary: AppColors.textWhite,
        onSurface: AppColors.textWhite,
        outline: AppColors.hairline,
      ),
      textTheme: GoogleFonts.spaceGroteskTextTheme(
        ThemeData.dark().textTheme,
      ).copyWith(
        displayLarge: GoogleFonts.syne(
          fontSize: 54,
          fontWeight: FontWeight.w700,
          letterSpacing: -1.8,
          color: AppColors.textWhite,
          height: 1.05,
        ),
        displayMedium: GoogleFonts.syne(
          fontSize: 40,
          fontWeight: FontWeight.w700,
          letterSpacing: -1.2,
          color: AppColors.textWhite,
          height: 1.1,
        ),
        headlineLarge: GoogleFonts.syne(
          fontSize: 30,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.8,
          color: AppColors.textWhite,
        ),
        headlineMedium: GoogleFonts.syne(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.4,
          color: AppColors.textWhite,
        ),
        headlineSmall: GoogleFonts.syne(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: AppColors.textWhite,
        ),
        titleLarge: GoogleFonts.spaceGrotesk(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          letterSpacing: -0.2,
          color: AppColors.textWhite,
        ),
        bodyLarge: GoogleFonts.spaceGrotesk(
          fontSize: 15,
          fontWeight: FontWeight.w400,
          color: AppColors.textWhite.withValues(alpha: 0.85),
        ),
        bodyMedium: GoogleFonts.spaceGrotesk(
          fontSize: 13,
          fontWeight: FontWeight.w400,
          color: AppColors.textMuted,
        ),
        labelSmall: GoogleFonts.jetBrainsMono(
          fontSize: 11,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.8,
          color: AppColors.textMuted,
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.hairline,
        thickness: 0.8,
        space: 1,
      ),
    );
  }
}
