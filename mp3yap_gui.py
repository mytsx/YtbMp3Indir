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
    # print("[MP3YAP] Starting application...")
    app = QApplication(sys.argv)
    app.setApplicationName("MP3 Yap")
    
    # Splash screen'i göster
    # print("[MP3YAP] Creating splash screen...")
    try:
        splash = SplashScreen()
        splash.start()  # start metodunu çağır
        # print("[MP3YAP] Splash screen displayed")
    except Exception as e:
        print(f"[MP3YAP ERROR] Failed to create splash screen: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Ana pencere değişkeni
    window = None
    
    # Gerçek yükleme işlemleri
    def load_application():
        nonlocal window
        
        try:
            # Modülleri import et (lazy loading)
            # print("[MP3YAP] Loading modules...")
            splash.update_status("Modüller yükleniyor...")
            from ui.main_window import MP3YapMainWindow
            app.processEvents()
        except Exception as e:
            print(f"[MP3YAP ERROR] Failed to load modules: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Uygulama hazır, splash'i kapat ve ana pencereyi göster
        splash.update_status("Hazır!")
        QTimer.singleShot(3000, show_main_window)  # 3 saniye bekle
        
    # Splash başladığında animasyonlar otomatik başlayacak
    
    # Yüklemeyi başlat
    QTimer.singleShot(1000, load_application)  # 1 saniye beklet ki animasyon görünsün
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()