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
from PyQt5.QtCore import Qt, QTimer
from ui.splash_screen import SplashScreen


def main():
    """Ana uygulama başlatıcı"""
    app = QApplication(sys.argv)
    app.setApplicationName("MP3 Yap")
    
    # Splash screen'i göster
    splash = SplashScreen()
    splash.show()
    
    # Gerçek yükleme işlemleri
    def load_application():
        # Modülleri import et (lazy loading)
        splash.update_status("Modüller yükleniyor...")
        from ui.main_window import MP3YapMainWindow
        app.processEvents()
        
        # Veritabanını kontrol et
        splash.update_status("Veritabanı hazırlanıyor...")
        from database.manager import DatabaseManager
        db = DatabaseManager()
        db.init_db()  # Veritabanı tablolarını oluştur
        app.processEvents()
        
        # Ayarları yükle
        splash.update_status("Ayarlar kontrol ediliyor...")
        from utils.config import Config
        config = Config()
        app.processEvents()
        
        # FFmpeg kontrolü
        splash.update_status("FFmpeg kontrol ediliyor...")
        import static_ffmpeg
        static_ffmpeg.add_paths()
        app.processEvents()
        
        # Ana pencereyi oluştur
        splash.update_status("Arayüz oluşturuluyor...")
        window = MP3YapMainWindow()
        app.processEvents()
        
        # Pencereyi göster
        def show_main_window():
            window.show()
            window.raise_()
            window.activateWindow()
        
        splash.finished.connect(show_main_window)
        
        # Animasyonları başlat
        QTimer.singleShot(100, splash.animate_boxes_fade_in)
        QTimer.singleShot(900, splash.start_color_wave_animation)
        QTimer.singleShot(2500, splash.animate_boxes_fade_out)
    
    # Yüklemeyi başlat
    QTimer.singleShot(100, load_application)
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()