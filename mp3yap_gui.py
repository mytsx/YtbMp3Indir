#!/usr/bin/env python3
"""
YouTube MP3 İndirici
Modern ve kullanıcı dostu YouTube'dan MP3 indirme aracı
"""

import sys
import os
import logging

# Modül yolunu ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from ui.splash_screen import SplashScreen

logger = logging.getLogger(__name__)


def main():
    """Ana uygulama başlatıcı"""
    # print("[MP3YAP] Starting application...")
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube MP3 İndirici")
    
    # Set application icon if it exists
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Splash screen'i göster
    # print("[MP3YAP] Creating splash screen...")
    try:
        splash = SplashScreen()
        splash.start()  # start metodunu çağır
        # print("[MP3YAP] Splash screen displayed")
    except Exception as e:
        logger.exception("Failed to create splash screen")
        sys.exit(1)
    
    # Ana pencere değişkeni
    window = None
    
    # Gerçek yükleme işlemleri
    def load_application():
        nonlocal window
        
        try:
            # Modülleri import et (lazy loading)
            # print("[MP3YAP] Loading modules...")
            # splash.update_status("Modüller yükleniyor...") # Translation manager not loaded yet
            from ui.main_window import MP3YapMainWindow
            app.processEvents()
        except Exception as e:
            logger.exception("Failed to load modules")
            return
        
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
        
        # Dil ayarlarını yükle
        splash.update_status("Dil ayarları yükleniyor...")
        from utils.translation_manager import translation_manager
        
        # Config'den dili al veya sistem dilini kullan
        saved_language = config.get('language', None)
        if saved_language:
            translation_manager.load_language(saved_language)
        else:
            # Sistem dilini kullan ve ilk kez kaydet
            system_language = translation_manager.get_system_language()
            translation_manager.load_language(system_language)
            config.set('language', system_language)
            # Config otomatik kaydediyor (set metodunda)
        
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
            if window:
                # Splash animasyonunu durdur
                if hasattr(splash, 'color_animation_timer') and splash.color_animation_timer:
                    splash.color_animation_timer.stop()
                splash.hide()  # Splash'i gizle
                splash.close()  # Splash'i kapat
                window.show()
                window.raise_()
                window.activateWindow()
                # print("[MP3YAP] Main window displayed")
        
        # Uygulama hazır, splash'i bilgilendir
        splash.update_status(translation_manager.tr("main.status.ready"))
        splash.set_app_ready()  # Logaritmik doldurma başlat
        
        # Ana pencereyi göster
        def final_show():
            if window:
                window.show()
                window.raise_()
                window.activateWindow()
        
        # Splash finished sinyalini dinle
        splash.finished.connect(final_show)
        
    # Splash başladığında animasyonlar otomatik başlayacak
    
    # Yüklemeyi başlat
    QTimer.singleShot(1000, load_application)  # 1 saniye beklet ki animasyon görünsün
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()