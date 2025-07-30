from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QSpinBox, QCheckBox,
                            QGroupBox, QFileDialog, QLineEdit, QTabWidget,
                            QWidget)
from PyQt5.QtCore import Qt
from utils.config import Config


class SettingsDialog(QDialog):
    """Uygulama ayarları penceresi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.setWindowTitle("Ayarlar")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Ayarlar arayüzünü oluştur"""
        layout = QVBoxLayout()
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # İndirme ayarları sekmesi
        download_tab = self.create_download_tab()
        self.tab_widget.addTab(download_tab, "İndirme")
        
        # Uygulama ayarları sekmesi
        app_tab = self.create_app_tab()
        self.tab_widget.addTab(app_tab, "Uygulama")
        
        layout.addWidget(self.tab_widget)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_download_tab(self):
        """İndirme ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Ses kalitesi
        quality_group = QGroupBox("Ses Ayarları")
        quality_layout = QVBoxLayout()
        
        quality_hlayout = QHBoxLayout()
        quality_hlayout.addWidget(QLabel("Ses Kalitesi:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128 kbps", "192 kbps", "320 kbps"])
        quality_hlayout.addWidget(self.quality_combo)
        quality_hlayout.addStretch()
        
        quality_layout.addLayout(quality_hlayout)
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)
        
        # İndirme klasörü
        folder_group = QGroupBox("İndirme Konumu")
        folder_layout = QVBoxLayout()
        
        folder_hlayout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_button = QPushButton("Gözat...")
        self.folder_button.clicked.connect(self.browse_folder)
        
        folder_hlayout.addWidget(self.folder_edit)
        folder_hlayout.addWidget(self.folder_button)
        
        folder_layout.addLayout(folder_hlayout)
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Performans ayarları
        perf_group = QGroupBox("Performans")
        perf_layout = QVBoxLayout()
        
        # Eşzamanlı indirme
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel("Eşzamanlı İndirme:"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setMinimum(1)
        self.concurrent_spin.setMaximum(5)
        concurrent_layout.addWidget(self.concurrent_spin)
        concurrent_layout.addStretch()
        
        perf_layout.addLayout(concurrent_layout)
        
        # Playlist limiti
        playlist_layout = QHBoxLayout()
        playlist_layout.addWidget(QLabel("Playlist Limiti:"))
        self.playlist_spin = QSpinBox()
        self.playlist_spin.setMinimum(0)
        self.playlist_spin.setMaximum(1000)
        self.playlist_spin.setSpecialValueText("Limitsiz")
        playlist_layout.addWidget(self.playlist_spin)
        playlist_layout.addStretch()
        
        perf_layout.addLayout(playlist_layout)
        
        # Otomatik yeniden deneme
        self.auto_retry_check = QCheckBox("Başarısız indirmeleri otomatik yeniden dene")
        perf_layout.addWidget(self.auto_retry_check)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_app_tab(self):
        """Uygulama ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Görünüm ayarları
        appearance_group = QGroupBox("Görünüm")
        appearance_layout = QVBoxLayout()
        
        # Tema
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        appearance_layout.addLayout(theme_layout)
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Bildirim ayarları
        notif_group = QGroupBox("Bildirimler")
        notif_layout = QVBoxLayout()
        
        self.notif_sound_check = QCheckBox("İndirme tamamlandığında ses çal")
        notif_layout.addWidget(self.notif_sound_check)
        
        self.auto_open_check = QCheckBox("İndirme sonrası klasörü otomatik aç")
        notif_layout.addWidget(self.auto_open_check)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Geçmiş ayarları
        history_group = QGroupBox("İndirme Geçmişi")
        history_layout = QVBoxLayout()
        
        history_hlayout = QHBoxLayout()
        history_hlayout.addWidget(QLabel("Geçmişi sakla:"))
        self.history_combo = QComboBox()
        self.history_combo.addItems(["30 gün", "60 gün", "90 gün", "Süresiz"])
        history_hlayout.addWidget(self.history_combo)
        history_hlayout.addStretch()
        
        history_layout.addLayout(history_hlayout)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def browse_folder(self):
        """İndirme klasörü seç"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "İndirme Klasörü Seç",
            self.folder_edit.text()
        )
        if folder:
            self.folder_edit.setText(folder)
    
    def load_settings(self):
        """Mevcut ayarları yükle"""
        # İndirme ayarları
        quality = self.config.get('audio_quality', '192')
        quality_index = {"128": 0, "192": 1, "320": 2}.get(quality, 1)
        self.quality_combo.setCurrentIndex(quality_index)
        
        self.folder_edit.setText(self.config.get('output_path', 'music'))
        self.concurrent_spin.setValue(self.config.get('max_simultaneous_downloads', 3))
        self.playlist_spin.setValue(self.config.get('playlist_limit', 0))
        self.auto_retry_check.setChecked(self.config.get('auto_retry', True))
        
        # Uygulama ayarları
        theme = self.config.get('theme', 'light')
        theme_index = 0 if theme == 'light' else 1
        self.theme_combo.setCurrentIndex(theme_index)
        
        self.notif_sound_check.setChecked(self.config.get('notification_sound', True))
        self.auto_open_check.setChecked(self.config.get('auto_open_folder', False))
        
        history_days = self.config.get('history_days', 0)
        history_map = {30: 0, 60: 1, 90: 2, 0: 3}
        self.history_combo.setCurrentIndex(history_map.get(history_days, 3))
    
    def save_settings(self):
        """Ayarları kaydet"""
        # İndirme ayarları
        quality_map = {0: "128", 1: "192", 2: "320"}
        self.config.set('audio_quality', quality_map[self.quality_combo.currentIndex()])
        self.config.set('output_path', self.folder_edit.text())
        self.config.set('max_simultaneous_downloads', self.concurrent_spin.value())
        self.config.set('playlist_limit', self.playlist_spin.value())
        self.config.set('auto_retry', self.auto_retry_check.isChecked())
        
        # Uygulama ayarları
        theme = 'light' if self.theme_combo.currentIndex() == 0 else 'dark'
        self.config.set('theme', theme)
        self.config.set('notification_sound', self.notif_sound_check.isChecked())
        self.config.set('auto_open_folder', self.auto_open_check.isChecked())
        
        history_map = {0: 30, 1: 60, 2: 90, 3: 0}
        self.config.set('history_days', history_map[self.history_combo.currentIndex()])
        
        self.accept()