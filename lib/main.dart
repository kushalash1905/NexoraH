import 'dart:ui';
import 'package:flutter/material.dart';
import 'screens/resume_gallery_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const RecruitRApp());
}

/// Custom scroll behavior enabling drag gestures with mouse and trackpad
/// on modern desktop browsers (Flutter Web).
class WebScrollBehavior extends MaterialScrollBehavior {
  @override
  Set<PointerDeviceKind> get dragDevices => {
        PointerDeviceKind.touch,
        PointerDeviceKind.mouse,
        PointerDeviceKind.trackpad,
        PointerDeviceKind.stylus,
      };
}

class RecruitRApp extends StatelessWidget {
  const RecruitRApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RecruitR — Smart Resume Shortlisting Engine',
      debugShowCheckedModeBanner: false,
      scrollBehavior: WebScrollBehavior(),
      theme: AppTheme.darkTheme,
      home: const ResumeGalleryScreen(),
    );
  }
}

// Backward compatibility alias
typedef NexoraApp = RecruitRApp;
