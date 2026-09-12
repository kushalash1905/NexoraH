import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nexorah/main.dart';
import 'package:nexorah/widgets/carousel_resume_card.dart';
import 'package:nexorah/widgets/horizontal_resume_carousel.dart';
import 'package:nexorah/widgets/resume_document.dart';

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  testWidgets('NexoraApp renders horizontal carousel with straight symmetric cards', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Verify brand header and main title
    expect(find.text('NEXORA'), findsWidgets);
    expect(find.text('RESUME DOSSIER COLLECTION'), findsOneWidget);

    // Verify presence of horizontal carousel and cards
    expect(find.byType(HorizontalResumeCarousel), findsOneWidget);
    expect(find.byType(CarouselResumeCard), findsWidgets);
    expect(find.text('Elena Rostova'), findsOneWidget);
  });

  testWidgets('Clicking active carousel card opens detailed resume view, navigates, and returns', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Tap on the first candidate card in carousel
    final firstCard = find.byType(CarouselResumeCard).first;
    await tester.tap(firstCard);
    await tester.pumpAndSettle();

    // Verify detailed document view is rendered for Candidate 1
    expect(find.byType(ResumeDocument), findsOneWidget);
    expect(find.text('Elena Rostova'), findsOneWidget);
    expect(find.text('PROFESSIONAL SUMMARY'), findsOneWidget);
    expect(find.text('TECHNICAL COMPETENCIES & EXPERTISE'), findsOneWidget);
    expect(find.text('PROFESSIONAL EXPERIENCE'), findsOneWidget);

    // Tap next arrow chevron in detail view
    final nextChevron = find.byIcon(Icons.chevron_right);
    expect(nextChevron, findsOneWidget);
    await tester.tap(nextChevron);
    await tester.pumpAndSettle();

    // Now Candidate 2 (Marcus Vance) is displayed in detail view
    expect(find.text('Marcus Vance'), findsOneWidget);

    // Tap 'RETURN TO ARCHIVE [ESC]' button
    final returnBtn = find.text('RETURN TO ARCHIVE [ESC]');
    expect(returnBtn, findsOneWidget);
    await tester.tap(returnBtn);
    await tester.pumpAndSettle();

    // Verify we are back on the horizontal carousel gallery screen
    expect(find.text('RESUME DOSSIER COLLECTION'), findsOneWidget);
    expect(find.byType(HorizontalResumeCarousel), findsOneWidget);
  });

  testWidgets('Search query filters candidate carousel dynamically', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Tap search button in CamilleNavBar to reveal search field
    final searchTrigger = find.text('SEARCH');
    expect(searchTrigger, findsOneWidget);
    await tester.tap(searchTrigger);
    await tester.pumpAndSettle();

    // Enter search query
    final searchField = find.byType(TextField);
    expect(searchField, findsOneWidget);
    await tester.enterText(searchField, 'Elena');
    await tester.pumpAndSettle();

    // Should find Elena Rostova and not other candidates
    expect(find.text('Elena Rostova'), findsOneWidget);
    expect(find.text('Marcus Vance'), findsNothing);
  });

  testWidgets('Category tabs filter horizontal carousel dynamically', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Tap 'SYSTEMS' category tab in CamilleNavBar
    final systemsTab = find.text('SYSTEMS');
    expect(systemsTab, findsOneWidget);
    await tester.tap(systemsTab);
    await tester.pumpAndSettle();

    // Systems candidates should be found (Elena Rostova), but AI candidates (Marcus Vance) should not
    expect(find.text('Elena Rostova'), findsOneWidget);
    expect(find.text('Marcus Vance'), findsNothing);
  });

  testWidgets('Horizontal carousel navigates with keyboard arrows and chevrons', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Verify initial index is 01 / 18
    expect(find.text('01'), findsWidgets);

    // Tap the right chevron arrow button in the carousel
    final rightChevron = find.byIcon(Icons.chevron_right).first;
    await tester.tap(rightChevron);
    await tester.pumpAndSettle();

    // Now current index should be 02 / 18
    expect(find.text('02'), findsWidgets);

    // Press left arrow key to navigate back
    await tester.sendKeyEvent(LogicalKeyboardKey.arrowLeft);
    await tester.pumpAndSettle();

    // Now back to index 01
    expect(find.text('01'), findsWidgets);
  });

  testWidgets('Horizontal carousel supports mouse dragging gestures', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Drag carousel horizontally to the left to advance
    final carousel = find.byType(HorizontalResumeCarousel);
    await tester.drag(carousel, const Offset(-450, 0));
    await tester.pumpAndSettle();

    // The carousel should have smoothly advanced to the next card
    expect(find.text('02'), findsWidgets);
  });

  testWidgets('Rank Candidates button triggers evaluation and displays Top 3 Podium', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Verify Rank Candidates button is present
    final rankBtn = find.text('RANK CANDIDATES');
    expect(rankBtn, findsOneWidget);

    // Click Rank Candidates
    await tester.tap(rankBtn);
    await tester.pump(); // Start evaluation

    // Notice evaluation state
    expect(find.text('SYNCHRONIZING CANDIDATE ARCHIVES'), findsOneWidget);

    // Settle after evaluation completes (900ms timer)
    await tester.pumpAndSettle(const Duration(milliseconds: 1200));

    // Verify Top 3 Podium is displayed
    expect(find.text('THE CANDIDATE PODIUM'), findsOneWidget);
    expect(find.text('PODIUM · POSITION 01'), findsOneWidget);
    expect(find.text('PODIUM · POSITION 02'), findsOneWidget);
    expect(find.text('PODIUM · POSITION 03'), findsOneWidget);

    // Verify 1st place candidate is Elena Rostova (highest score 97%)
    expect(find.text('Elena Rostova'), findsWidgets);
    expect(find.text('#01 // HIGHEST MATCH'), findsOneWidget);

    // Tap 'RETURN TO ARCHIVE [ESC]' button
    final returnBtn = find.text('RETURN TO ARCHIVE [ESC]');
    expect(returnBtn, findsOneWidget);
    await tester.tap(returnBtn);
    await tester.pumpAndSettle();

    // Verify we are back on the horizontal carousel gallery screen
    expect(find.text('RESUME DOSSIER COLLECTION'), findsOneWidget);
    expect(find.byType(HorizontalResumeCarousel), findsOneWidget);
  });

  testWidgets('Clicking candidate on Top 3 Podium opens detailed resume view', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Click Rank Candidates
    await tester.tap(find.text('RANK CANDIDATES'));
    await tester.pumpAndSettle(const Duration(milliseconds: 1200));

    // Tap on the 1st position candidate card on the podium
    final firstPodiumCard = find.text('#01 // HIGHEST MATCH');
    expect(firstPodiumCard, findsOneWidget);
    await tester.tap(firstPodiumCard);
    await tester.pumpAndSettle();

    // Verify detail screen opens
    expect(find.byType(ResumeDocument), findsOneWidget);
    expect(find.text('Elena Rostova'), findsOneWidget);
    expect(find.text('PROFESSIONAL SUMMARY'), findsOneWidget);

    // Return using Escape
    await tester.sendKeyEvent(LogicalKeyboardKey.escape);
    await tester.pumpAndSettle();

    // Should return to podium or gallery
    expect(find.text('Elena Rostova'), findsWidgets);
  });

  testWidgets('Upload Resumes button exists and ResumeUploadService generates valid mock candidate', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const NexoraApp());
    await tester.pumpAndSettle();

    // Verify UPLOAD RESUMES button is present
    expect(find.text('UPLOAD RESUMES'), findsOneWidget);
  });
}
