#!/usr/bin/env python3
"""
YouTube MP3 İndirici - No Splash Version
Splash screen olmadan doğrudan açılan versiyon
"""

import sys
import os

# macOS environment variables
if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MP3YapMainWindow
from database.manager import DatabaseManager
from utils.ffmpeg_helper import setup_ffmpeg


def main():
    """Ana uygulama başlatıcı - splash screen olmadan"""
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube MP3 İndirici")
    
    # Set application icon if it exists
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Veritabanı başlat
    db = DatabaseManager()
    db.init_db()
    
    # FFmpeg kurulumunu kontrol et
    setup_ffmpeg()
    
    # Ana pencereyi oluştur ve göster
    window = MP3YapMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()