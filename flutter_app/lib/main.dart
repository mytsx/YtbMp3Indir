import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/download/screens/download_screen.dart';
import 'features/history/screens/history_screen.dart';
import 'features/settings/screens/settings_screen.dart';
import 'core/providers/providers.dart';
import 'core/services/backend_service.dart';

// Global reference to stop backend on app exit
late final ProviderContainer _container;
late final BackendService _backendService;
bool _isShuttingDown = false;

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

void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Create provider container to start backend
  _container = ProviderContainer();

  // Start backend automatically
  print('🚀 Starting backend...');
  _backendService = _container.read(backendServiceProvider);

  try {
    await _backendService.start();
    print('✅ Backend started successfully');
  } catch (e) {
    print('❌ Failed to start backend: $e');
    print('⚠️ App will continue but may not work properly');
  }

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

  // Run the app
  runApp(
    UncontrolledProviderScope(
      container: _container,
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
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
    return MaterialApp(
      title: 'MP3 Yap',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      home: const MainNavigation(),
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
