#!/usr/bin/env python3
"""
YouTube MP3 İndirici - macOS Version (No Splash)
Splash screen olmadan doğrudan açılan macOS versiyonu
"""

import sys
import os

# Sadece macOS'ta çalıştır
if sys.platform != 'darwin':
    print("This version is for macOS only!")
    sys.exit(1)

# macOS için gerekli çevre değişkenleri
os.environ['QT_MAC_WANTS_LAYER'] = '1'
os.environ['PYQT_DISABLE_MAIN_THREAD_CHECKER'] = '1'

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


def main():
    """Ana uygulama başlatıcı - splash screen olmadan"""
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube MP3 İndirici")
    
    # Set application icon if it exists
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Doğrudan ana pencereyi yükle
    try:
        from ui.main_window import MP3YapMainWindow
        from database.manager import DatabaseManager
        from utils.ffmpeg_helper import setup_ffmpeg
        
        # Veritabanı başlat
        db = DatabaseManager()
        
        # FFmpeg kurulumunu kontrol et
        setup_ffmpeg()
        
        # Ana pencereyi oluştur ve göster
        window = MP3YapMainWindow()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()