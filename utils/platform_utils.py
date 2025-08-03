"""Platform-specific utilities for MP3Yap"""
import platform
from PyQt5.QtGui import QKeySequence


def get_platform():
    """Get current platform"""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    else:
        return "linux"


def get_keyboard_icon():
    """Get platform-specific keyboard icon name"""
    system = get_platform()
    if system == "macos":
        return "command"
    elif system == "windows":
        return "windows"  # Eğer windows.svg yoksa keyboard.svg kullanılacak
    else:
        return "keyboard"


def get_modifier_key():
    """Get platform-specific modifier key name"""
    system = get_platform()
    if system == "macos":
        return "Cmd"
    else:
        return "Ctrl"


def get_modifier_symbol():
    """Get platform-specific modifier key symbol"""
    system = get_platform()
    if system == "macos":
        return "⌘"
    else:
        return "Ctrl"


def convert_shortcut_for_platform(shortcut_str):
    """Convert shortcut string to platform-specific format"""
    system = get_platform()
    
    if system == "macos":
        # Windows/Linux to Mac conversion
        shortcut_str = shortcut_str.replace("Ctrl+", "Cmd+")
        shortcut_str = shortcut_str.replace("Ctrl-", "Cmd-")
    else:
        # Mac to Windows/Linux conversion
        shortcut_str = shortcut_str.replace("Cmd+", "Ctrl+")
        shortcut_str = shortcut_str.replace("Cmd-", "Ctrl-")
        shortcut_str = shortcut_str.replace("⌘", "Ctrl")
    
    return shortcut_str


def get_platform_shortcut_display(key_sequence):
    """Get platform-appropriate shortcut display string"""
    if isinstance(key_sequence, QKeySequence.StandardKey):
        # Convert StandardKey to QKeySequence first
        key_sequence = QKeySequence(key_sequence)
    
    # Get native text representation
    native_text = key_sequence.toString(QKeySequence.NativeText)
    
    # Platform-specific conversions
    system = get_platform()
    if system == "macos":
        # Mac already shows native format correctly
        return native_text
    else:
        # Windows/Linux - ensure Ctrl is used instead of Cmd
        return native_text.replace("Meta+", "Ctrl+")