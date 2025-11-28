import Cocoa
import FlutterMacOS

@main
class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }

  override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
    return true
  }

  override func applicationWillTerminate(_ notification: Notification) {
    // Kill backend process on app termination
    killBackendProcess()
    super.applicationWillTerminate(notification)
  }

  private func killBackendProcess() {
    // Find project root by looking for .backend_pid file
    let fileManager = FileManager.default
    var currentPath = fileManager.currentDirectoryPath

    // Try to find .backend_pid in parent directories
    for _ in 0..<10 {
      let pidFilePath = (currentPath as NSString).appendingPathComponent(".backend_pid")
      if fileManager.fileExists(atPath: pidFilePath) {
        do {
          let pidString = try String(contentsOfFile: pidFilePath, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
          if let pid = Int32(pidString) {
            print("Killing backend process with PID: \(pid)")
            kill(pid, SIGTERM)

            // Also clean up the PID file
            try? fileManager.removeItem(atPath: pidFilePath)

            // Clean up port file too
            let portFilePath = (currentPath as NSString).appendingPathComponent(".backend_port")
            try? fileManager.removeItem(atPath: portFilePath)
          }
        } catch {
          print("Error reading PID file: \(error)")
        }
        return
      }

      // Go up one directory
      currentPath = (currentPath as NSString).deletingLastPathComponent
    }

    // Fallback: Try from executable path
    if let executablePath = Bundle.main.executablePath {
      var searchPath = (executablePath as NSString).deletingLastPathComponent
      for _ in 0..<10 {
        let pidFilePath = (searchPath as NSString).appendingPathComponent(".backend_pid")
        if fileManager.fileExists(atPath: pidFilePath) {
          do {
            let pidString = try String(contentsOfFile: pidFilePath, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
            if let pid = Int32(pidString) {
              print("Killing backend process with PID: \(pid)")
              kill(pid, SIGTERM)
              try? fileManager.removeItem(atPath: pidFilePath)
            }
          } catch {
            print("Error reading PID file: \(error)")
          }
          return
        }
        searchPath = (searchPath as NSString).deletingLastPathComponent
      }
    }

    print("Backend PID file not found, backend may still be running")
  }
}
