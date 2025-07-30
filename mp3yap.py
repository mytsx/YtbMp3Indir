#!/usr/bin/env python3
"""
MP3 Yap - YouTube İndirici
Modern ve kullanıcı dostu YouTube MP3 indirici
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MP3YapMainWindow


def main():
    """Ana uygulama başlatıcı"""
    app = QApplication(sys.argv)
    app.setApplicationName("MP3 Yap")
    app.setOrganizationName("MP3Yap")
    
    # Ana pencereyi oluştur ve göster
    window = MP3YapMainWindow()
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()