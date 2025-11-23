import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mp3yap/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: MyApp(),
      ),
    );

    // Verify navigation bar exists
    expect(find.text('Download'), findsOneWidget);
    expect(find.text('History'), findsOneWidget);
    expect(find.text('Settings'), findsOneWidget);
  });

  testWidgets('Navigation works', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MyApp(),
      ),
    );

    // Tap history tab
    await tester.tap(find.text('History'));
    await tester.pumpAndSettle();

    // Verify history screen is shown
    expect(find.text('Download History'), findsOneWidget);

    // Tap settings tab
    await tester.tap(find.text('Settings'));
    await tester.pumpAndSettle();

    // Verify settings screen is shown
    expect(find.text('Audio Quality'), findsOneWidget);
  });
}
