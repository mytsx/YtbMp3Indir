import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/download/screens/download_screen.dart';
import 'features/convert/screens/convert_screen.dart';
import 'features/history/screens/history_screen.dart';
import 'features/settings/screens/settings_screen.dart';
import 'features/splash/screens/splash_screen.dart';
import 'core/providers/providers.dart';
import 'core/services/backend_service.dart';

// Global reference to stop backend on app exit
late final ProviderContainer _container;
late final BackendService _backendService;
bool _isShuttingDown = false;
bool _backendStarted = false;

Future<void> _shutdownBackend() async {
  if (_isShuttingDown) return;
  _isShuttingDown = true;

  print('🛑 Shutting down backend...');
  try {
    await _backendService.stop();
    _container.dispose();
    print('✅ Backend stopped successfully');
  } catch (e) {
    print('❌ Error stopping backend: $e');
  }
}

Future<void> _startBackend() async {
  if (_backendStarted) return;

  print('🚀 Starting backend...');
  _backendService = _container.read(backendServiceProvider);

  try {
    await _backendService.start();
    _backendStarted = true;
    print('✅ Backend started successfully');
  } catch (e) {
    print('❌ Failed to start backend: $e');
    print('⚠️ App will continue but may not work properly');
  }
}

void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Create provider container
  _container = ProviderContainer();

  // Handle process signals for graceful shutdown (desktop)
  if (Platform.isMacOS || Platform.isLinux || Platform.isWindows) {
    // Handle SIGINT (Ctrl+C)
    ProcessSignal.sigint.watch().listen((_) async {
      print('Received SIGINT');
      await _shutdownBackend();
      exit(0);
    });

    // Handle SIGTERM (kill command)
    if (!Platform.isWindows) {
      ProcessSignal.sigterm.watch().listen((_) async {
        print('Received SIGTERM');
        await _shutdownBackend();
        exit(0);
      });
    }
  }

  // Run the app (backend will be started from splash screen)
  runApp(
    UncontrolledProviderScope(
      container: _container,
      child: const MyApp(),
    ),
  );
}

class MyApp extends ConsumerStatefulWidget {
  const MyApp({super.key});

  @override
  ConsumerState<MyApp> createState() => _MyAppState();
}

class _MyAppState extends ConsumerState<MyApp> with WidgetsBindingObserver {
  bool _showSplash = true;
  String _splashStatus = 'Starting...';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    // Start backend
    setState(() => _splashStatus = 'Starting backend...');
    await _startBackend();

    // Small delay to show the animation
    await Future.delayed(const Duration(milliseconds: 500));

    // Hide splash screen
    if (mounted) {
      setState(() {
        _splashStatus = 'Ready!';
      });

      await Future.delayed(const Duration(milliseconds: 300));

      if (mounted) {
        setState(() => _showSplash = false);
      }
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    // Stop backend when app is disposed
    _stopBackend();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    print('App lifecycle state: $state');

    // Stop backend when app is detached (closed)
    if (state == AppLifecycleState.detached) {
      _stopBackend();
    }
  }

  void _stopBackend() {
    _shutdownBackend();
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp(
      title: 'MP3 Yap',
      debugShowCheckedModeBanner: false,
      themeMode: themeMode,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: _showSplash
          ? SplashScreen(
              statusMessage: _splashStatus,
              onFinished: () => setState(() => _showSplash = false),
            )
          : const MainNavigation(),
    );
  }
}

/// Main navigation with bottom navigation bar
class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    DownloadScreen(),
    ConvertScreen(),
    HistoryScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.download_outlined),
            selectedIcon: Icon(Icons.download),
            label: 'Download',
          ),
          NavigationDestination(
            icon: Icon(Icons.transform_outlined),
            selectedIcon: Icon(Icons.transform),
            label: 'Convert',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}
