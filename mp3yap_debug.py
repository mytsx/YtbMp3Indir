#!/usr/bin/env python3
"""
YouTube MP3 İndirici - Debug Version
Crash debug için detaylı log yazan versiyon
"""

import sys
import os
import traceback
from datetime import datetime

# Debug log dosyası
debug_log = os.path.expanduser("~/Desktop/mp3yap_debug.log")

def debug_write(msg):
    """Debug mesajı yaz"""
    with open(debug_log, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
        f.flush()

debug_write("=== MP3Yap Debug Starting ===")
debug_write(f"Python: {sys.version}")
debug_write(f"Platform: {sys.platform}")
debug_write(f"Frozen: {getattr(sys, 'frozen', False)}")
debug_write(f"Executable: {sys.executable}")

try:
    # macOS environment variables
    if sys.platform == 'darwin':
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        debug_write("Set QT_MAC_WANTS_LAYER=1")

    # Modül yolunu ekle
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    debug_write(f"Added path: {os.path.dirname(os.path.abspath(__file__))}")

    debug_write("Importing PyQt5...")
    from PyQt5.QtWidgets import QApplication
    debug_write("Imported QApplication")
    
    from PyQt5.QtGui import QIcon
    debug_write("Imported QIcon")
    
    from PyQt5.QtCore import QTimer
    debug_write("Imported QTimer")

    debug_write("Importing ui.main_window...")
    from ui.main_window import MP3YapMainWindow
    debug_write("Imported MP3YapMainWindow")
    
    debug_write("Importing database.manager...")
    from database.manager import DatabaseManager
    debug_write("Imported DatabaseManager")
    
    debug_write("Importing utils.ffmpeg_helper...")
    from utils.ffmpeg_helper import setup_ffmpeg
    debug_write("Imported setup_ffmpeg")

except Exception as e:
    debug_write(f"Import Error: {str(e)}")
    debug_write(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

def main():
    """Ana uygulama başlatıcı - debug version"""
    try:
        debug_write("Creating QApplication...")
        app = QApplication(sys.argv)
        debug_write("QApplication created")
        
        app.setApplicationName("YouTube MP3 İndirici")
        debug_write("Set application name")
        
        # Set application icon if it exists
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            debug_write(f"Set icon from: {icon_path}")
        else:
            debug_write(f"Icon not found at: {icon_path}")
        
        # Veritabanı başlat
        debug_write("Initializing database...")
        db = DatabaseManager()
        db.init_db()
        debug_write("Database initialized")
        
        # FFmpeg kurulumunu kontrol et
        debug_write("Setting up FFmpeg...")
        setup_ffmpeg()
        debug_write("FFmpeg setup complete")
        
        # Ana pencereyi oluştur ve göster
        debug_write("Creating main window...")
        window = MP3YapMainWindow()
        debug_write("Main window created")
        
        debug_write("Showing main window...")
        window.show()
        debug_write("Main window shown")
        
        # Test: Basit bir timer ekle
        def test_timer():
            debug_write("Timer tick!")
        
        timer = QTimer()
        timer.timeout.connect(test_timer)
        timer.start(5000)  # 5 saniyede bir
        debug_write("Timer started")
        
        debug_write("Starting event loop...")
        result = app.exec_()
        debug_write(f"Event loop exited with code: {result}")
        
        sys.exit(result)
        
    except Exception as e:
        debug_write(f"Main Error: {str(e)}")
        debug_write(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == '__main__':
    main()