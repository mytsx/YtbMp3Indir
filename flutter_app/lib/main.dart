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
import 'shared/widgets/animated_nav_bar.dart';
import 'shared/widgets/glassmorphic_card.dart';
import 'core/providers/providers.dart';
import 'core/services/backend_service.dart';
import 'core/services/settings_service.dart';
import 'core/theme/cyberpunk_theme.dart';

// Global reference to stop backend on app exit
late final ProviderContainer _container;
late final BackendService _backendService;
late final SettingsService _settingsService;
bool _isShuttingDown = false;
bool _backendStarted = false;

Future<void> _shutdownBackend() async {
  if (_isShuttingDown) return;
  _isShuttingDown = true;

  debugPrint('🛑 Shutting down backend...');
  try {
    await _backendService.stop();
    debugPrint('✅ Backend stopped successfully');
  } catch (e) {
    debugPrint('❌ Error stopping backend: $e');
  }

  // Dispose container after backend is stopped
  try {
    _container.dispose();
  } catch (e) {
    debugPrint('Warning: Error disposing container: $e');
  }
}

Future<void> _startBackend() async {
  if (_backendStarted) return;

  debugPrint('🚀 Starting backend...');
  _backendService = _container.read(backendServiceProvider);

  try {
    await _backendService.start();
    _backendStarted = true;
    debugPrint('✅ Backend started successfully');
  } catch (e) {
    debugPrint('❌ Failed to start backend: $e');
    debugPrint('⚠️ App will continue but may not work properly');
  }
}

void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize settings service (SharedPreferences)
  _settingsService = SettingsService();
  await _settingsService.init();

  // Create provider container with pre-initialized settings service
  _container = ProviderContainer(
    overrides: [
      settingsServiceProvider.overrideWithValue(_settingsService),
    ],
  );

  // Handle process signals for graceful shutdown (desktop)
  if (Platform.isMacOS || Platform.isLinux || Platform.isWindows) {
    // Handle SIGINT (Ctrl+C)
    ProcessSignal.sigint.watch().listen((_) async {
      debugPrint('Received SIGINT');
      await _shutdownBackend();
      exit(0);
    });

    // Handle SIGTERM (kill command)
    if (!Platform.isWindows) {
      ProcessSignal.sigterm.watch().listen((_) async {
        debugPrint('Received SIGTERM');
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
  static const _windowChannel = MethodChannel('mp3yap/window');
  bool _showSplash = true;
  String _splashMessage = 'Starting backend service...';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    // Start backend
    if (mounted) setState(() => _splashMessage = 'Starting backend service...');
    await _startBackend();

    // Small delay to show the animation
    if (mounted) setState(() => _splashMessage = 'Initializing application...');
    await Future.delayed(const Duration(milliseconds: 800));

    if (mounted) setState(() => _splashMessage = 'Ready!');
    await Future.delayed(const Duration(milliseconds: 200));

    // Make window opaque before hiding splash
    if (Platform.isMacOS) {
      await _windowChannel.invokeMethod('setOpaque', true);
    }

    // Hide splash screen
    if (mounted) {
      setState(() => _showSplash = false);
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
    debugPrint('App lifecycle state: $state');

    // Stop backend when app is detached (closed)
    if (state == AppLifecycleState.detached) {
      _stopBackend();
    }
  }

  void _stopBackend() {
    _shutdownBackend();
  }

  void _updateWindowAppearance(ThemeMode mode) {
    if (!Platform.isMacOS) return;

    String appearance;
    switch (mode) {
      case ThemeMode.dark:
        appearance = 'dark';
        break;
      case ThemeMode.light:
        appearance = 'light';
        break;
      case ThemeMode.system:
        appearance = 'system';
        break;
    }

    _windowChannel.invokeMethod('setAppearance', appearance);
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = ref.watch(themeModeProvider);
    final themeStyle = ref.watch(themeStyleProvider);

    // Update window appearance when theme changes
    _updateWindowAppearance(themeMode);

    ThemeData lightTheme;
    ThemeData darkTheme;

    if (themeStyle == 'cyberpunk') {
      lightTheme = CyberpunkTheme.lightTheme;
      darkTheme = CyberpunkTheme.darkTheme;
    } else {
      // Classic Theme
      lightTheme = ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      );
      darkTheme = ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.dark,
        ),
      );
    }

    return MaterialApp(
      title: 'MP3 Yap',
      debugShowCheckedModeBanner: false,
      themeMode: themeMode,
      theme: lightTheme,
      darkTheme: darkTheme,
      // Disable theme animation to prevent TextStyle.lerp errors
      // when switching between theme styles with different inherit values
      themeAnimationDuration: Duration.zero,
      home: _showSplash
          ? SplashScreen(message: _splashMessage)
          : const MainNavigation(),
    );
  }
}

/// Main navigation with bottom navigation bar
class MainNavigation extends ConsumerStatefulWidget {
  const MainNavigation({super.key});

  @override
  ConsumerState<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends ConsumerState<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    DownloadScreen(),
    HistoryScreen(),
    ConvertScreen(),
    SettingsScreen(),
  ];

  static const _navItems = [
    NavItem(
      icon: Icons.download_outlined,
      selectedIcon: Icons.download,
      label: 'Download',
    ),
    NavItem(
      icon: Icons.history_outlined,
      selectedIcon: Icons.history,
      label: 'History',
    ),
    NavItem(
      icon: Icons.transform_outlined,
      selectedIcon: Icons.transform,
      label: 'Convert',
    ),
    NavItem(
      icon: Icons.settings_outlined,
      selectedIcon: Icons.settings,
      label: 'Settings',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final themeStyle = ref.watch(themeStyleProvider);
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    if (themeStyle == 'cyberpunk') {
      // Cyberpunk dark mode: use animated background
      if (isDarkMode) {
        return CyberpunkBackground(
          child: Scaffold(
            backgroundColor: Colors.transparent,
            body: IndexedStack(
              index: _currentIndex,
              children: _screens,
            ),
            bottomNavigationBar: AnimatedNavBar(
              currentIndex: _currentIndex,
              items: _navItems,
              onTap: (index) {
                setState(() {
                  _currentIndex = index;
                });
              },
            ),
          ),
        );
      }
      // Cyberpunk light mode: use standard scaffold with AnimatedNavBar
      return Scaffold(
        body: IndexedStack(
          index: _currentIndex,
          children: _screens,
        ),
        bottomNavigationBar: AnimatedNavBar(
          currentIndex: _currentIndex,
          items: _navItems,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
        ),
      );
    } else {
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
              icon: Icon(Icons.history_outlined),
              selectedIcon: Icon(Icons.history),
              label: 'History',
            ),
            NavigationDestination(
              icon: Icon(Icons.transform_outlined),
              selectedIcon: Icon(Icons.transform),
              label: 'Convert',
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
}
