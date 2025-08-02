#!/usr/bin/env python3
"""
MP3Yap Launcher - Terminal'siz başlatıcı
"""

import subprocess
import sys
import os

def main():
    # Uygulama yolunu bul
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle içinde
        bundle_dir = sys._MEIPASS
        app_path = os.path.join(os.path.dirname(sys.executable), "MP3Yap_Main")
    else:
        # Development mode
        app_path = os.path.join(os.path.dirname(__file__), "mp3yap_gui_nosplash.py")
        
    # Uygulamayı arka planda başlat
    if sys.platform == 'darwin':
        # macOS - Terminal'siz başlat
        subprocess.Popen([sys.executable, app_path], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True)
    else:
        # Diğer platformlar
        subprocess.Popen([sys.executable, app_path])
    
    # Launcher'ı kapat
    sys.exit(0)

if __name__ == "__main__":
    main()