import 'dart:ui';
import 'package:flutter/material.dart';
import 'screens/resume_gallery_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const NexoraApp());
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

class NexoraApp extends StatelessWidget {
  const NexoraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NexoraH — Smart Resume Shortlisting Engine',
      debugShowCheckedModeBanner: false,
      scrollBehavior: WebScrollBehavior(),
      theme: AppTheme.darkTheme,
      home: const ResumeGalleryScreen(),
    );
  }
}
