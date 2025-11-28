import 'package:flutter/foundation.dart';

/// Global error handler for uncaught errors
class ErrorHandler {
  static void init() {
    // Catch Flutter framework errors
    FlutterError.onError = (FlutterErrorDetails details) {
      FlutterError.presentError(details);
      _logError(details.exception, details.stack);
    };

    // Catch async errors (commented out - requires dart:ui import)
    // PlatformDispatcher.instance.onError = (error, stack) {
    //   _logError(error, stack);
    //   return true;
    // };
  }

  static void _logError(Object error, StackTrace? stack) {
    // In production, send to crash reporting service
    debugPrint('=== ERROR ===');
    debugPrint(error.toString());
    if (stack != null) {
      debugPrint(stack.toString());
    }
    debugPrint('=============');
  }
}
