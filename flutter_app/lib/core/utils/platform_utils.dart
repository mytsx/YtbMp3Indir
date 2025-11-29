import 'dart:io';

/// Open file location in system file manager
/// - macOS: Opens Finder with file selected
/// - Windows: Opens Explorer with file selected
/// - Linux: Opens file manager in the directory
Future<void> openInFolder(String filePath) async {
  final file = File(filePath);
  final directory = file.parent.path;

  if (Platform.isMacOS) {
    await Process.run('open', ['-R', filePath]);
  } else if (Platform.isWindows) {
    await Process.run('explorer', ['/select,', filePath]);
  } else if (Platform.isLinux) {
    await Process.run('xdg-open', [directory]);
  } else {
    throw UnsupportedError('openInFolder is not supported on this platform.');
  }
}

/// Open URL in default browser
/// Uses platform-specific commands instead of url_launcher
/// (url_launcher has issues with macOS sandbox)
Future<void> openUrl(String url) async {
  if (Platform.isMacOS) {
    await Process.run('open', [url]);
  } else if (Platform.isWindows) {
    await Process.run('start', [url], runInShell: true);
  } else if (Platform.isLinux) {
    await Process.run('xdg-open', [url]);
  } else {
    throw UnsupportedError('openUrl is not supported on this platform.');
  }
}
