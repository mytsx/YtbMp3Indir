import Cocoa
import FlutterMacOS

class MainFlutterWindow: NSWindow {
  private var methodChannel: FlutterMethodChannel?

  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    flutterViewController.backgroundColor = .clear
    let windowFrame = self.frame
    self.contentViewController = flutterViewController
    self.setFrame(windowFrame, display: true)

    // Set minimum window size to prevent overflow
    self.minSize = NSSize(width: 800, height: 700)

    // Set initial window size
    self.setContentSize(NSSize(width: 1000, height: 750))

    // Center window on screen
    self.center()

    // Start with transparent window for splash
    self.isOpaque = false
    self.backgroundColor = .clear
    self.hasShadow = false
    self.styleMask = self.styleMask.union(.fullSizeContentView)
    self.titlebarAppearsTransparent = true
    self.titleVisibility = .hidden
    self.standardWindowButton(.closeButton)?.isHidden = true
    self.standardWindowButton(.miniaturizeButton)?.isHidden = true
    self.standardWindowButton(.zoomButton)?.isHidden = true

    // Setup method channel for window transparency control
    methodChannel = FlutterMethodChannel(
      name: "mp3yap/window",
      binaryMessenger: flutterViewController.engine.binaryMessenger
    )

    methodChannel?.setMethodCallHandler { [weak self] (call, result) in
      switch call.method {
      case "setOpaque":
        if let isOpaque = call.arguments as? Bool {
          DispatchQueue.main.async {
            guard let self = self else { return }
            self.isOpaque = isOpaque
            self.backgroundColor = isOpaque ? .windowBackgroundColor : .clear
            self.hasShadow = isOpaque
            
            if isOpaque {
                self.styleMask.remove(.fullSizeContentView)
                self.titlebarAppearsTransparent = false
                self.titleVisibility = .visible
                self.standardWindowButton(.closeButton)?.isHidden = false
                self.standardWindowButton(.miniaturizeButton)?.isHidden = false
                self.standardWindowButton(.zoomButton)?.isHidden = false
            }
            
            self.invalidateShadow()
          }
        }
        result(nil)
      case "setAppearance":
        if let appearanceName = call.arguments as? String {
          DispatchQueue.main.async {
            guard let self = self else { return }
            if appearanceName == "dark" {
              self.appearance = NSAppearance(named: .darkAqua)
            } else if appearanceName == "light" {
              self.appearance = NSAppearance(named: .aqua)
            } else {
              self.appearance = nil // System default
            }
          }
        }
        result(nil)
      default:
        result(FlutterMethodNotImplemented)
      }
    }

    RegisterGeneratedPlugins(registry: flutterViewController)

    super.awakeFromNib()
  }
}
