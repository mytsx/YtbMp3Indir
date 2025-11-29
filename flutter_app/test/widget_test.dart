import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mp3yap/features/download/screens/download_screen.dart';
import 'package:mp3yap/core/services/settings_service.dart';
import 'package:mp3yap/core/providers/providers.dart';

void main() {
  late SettingsService settingsService;

  setUpAll(() {
    SharedPreferences.setMockInitialValues({});
  });

  setUp(() async {
    settingsService = SettingsService();
    await settingsService.init();
  });

  Widget createWidgetUnderTest() {
    return ProviderScope(
      overrides: [
        settingsServiceProvider.overrideWithValue(settingsService),
      ],
      child: const MaterialApp(
        home: DownloadScreen(),
      ),
    );
  }

  group('Download Screen Widget Tests', () {
    testWidgets('Download screen shows URL input field',
        (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Verify URL input exists
      expect(find.text('YouTube URL'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget);
    });

    testWidgets('Download screen shows start button',
        (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Verify download button exists
      expect(find.text('Start Download'), findsOneWidget);
    });

    testWidgets('Download screen shows active downloads section',
        (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Verify active downloads section exists
      expect(find.text('Downloads'), findsOneWidget);
    });

    testWidgets('Empty state shows message when no downloads',
        (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Verify empty state message
      expect(find.text('No downloads yet'), findsOneWidget);
    });

    testWidgets('URL validation shows error for empty input',
        (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Tap download button without entering URL
      await tester.tap(find.text('Start Download'));
      await tester.pump();

      // Should show error message
      expect(find.text('Please enter a YouTube URL'), findsOneWidget);
    });

    testWidgets('URL validation shows error for invalid URL',
        (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Enter invalid URL
      await tester.enterText(find.byType(TextField), 'not-a-youtube-url');
      await tester.tap(find.text('Start Download'));
      await tester.pump();

      // Should show error message
      expect(find.text('Please enter a valid YouTube URL'), findsOneWidget);
    });
  });
}
