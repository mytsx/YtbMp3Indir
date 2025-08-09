#!/usr/bin/env python3
"""Test translation system"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTranslator

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("İndir"))
        
        # Create central widget
        central = QWidget()
        layout = QVBoxLayout()
        
        # Add test labels
        layout.addWidget(QLabel(self.tr("İndir")))
        layout.addWidget(QLabel(self.tr("Geçmiş")))
        layout.addWidget(QLabel(self.tr("Sıra")))
        layout.addWidget(QLabel(self.tr("Ayarlar")))
        
        # Add button to switch language
        self.lang_button = QPushButton("Switch to English")
        self.lang_button.clicked.connect(self.switch_language)
        layout.addWidget(self.lang_button)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        self.translator = QTranslator()
        self.current_lang = 'tr'
    
    def switch_language(self):
        app = QApplication.instance()
        
        if self.current_lang == 'tr':
            # Load English
            translation_file = "/Users/yerli/Developer/mehmetyerli/mp3yap/translations/mp3yap_en.qm"
            if os.path.exists(translation_file):
                if self.translator.load(translation_file):
                    app.installTranslator(self.translator)
                    print(f"Loaded: {translation_file}")
                    self.current_lang = 'en'
                    self.lang_button.setText("Switch to Turkish")
                else:
                    print(f"Failed to load: {translation_file}")
            else:
                print(f"File not found: {translation_file}")
        else:
            # Remove English, go back to Turkish
            app.removeTranslator(self.translator)
            self.current_lang = 'tr'
            self.lang_button.setText("Switch to English")
        
        # Force UI update
        self.retranslateUi()
    
    def retranslateUi(self):
        """Update UI with new translations"""
        self.setWindowTitle(self.tr("İndir"))
        # Note: We'd need to keep references to labels to update them

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())