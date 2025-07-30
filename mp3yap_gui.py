#!/usr/bin/env python3
"""
MP3 Yap GUI - YouTube MP3 İndirici
Modern ve kullanıcı dostu YouTube'dan MP3 indirme aracı
"""

import sys
import os

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MP3YapMainWindow
from ui.splash_screen import SplashScreen


def main():
    """Ana uygulama başlatıcı"""
    app = QApplication(sys.argv)
    app.setApplicationName("MP3 Yap")
    
    # Splash screen'i göster
    splash = SplashScreen()
    
    # Ana pencereyi oluştur (gizli)
    window = MP3YapMainWindow()
    
    # Splash screen bittiğinde ana pencereyi göster
    def show_main_window():
        window.show()
        # Pencereyi öne getir
        window.raise_()
        window.activateWindow()
    
    splash.finished.connect(show_main_window)
    splash.start()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()