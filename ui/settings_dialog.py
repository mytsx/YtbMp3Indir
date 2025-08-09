from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QSpinBox, QCheckBox,
                           QGroupBox, QFileDialog, QLineEdit, QTabWidget,
                           QWidget)
from PyQt5.QtCore import Qt
from utils.config import Config
from styles import style_manager
from utils.icon_manager import icon_manager
from utils.translation_manager import translation_manager


class SettingsDialog(QDialog):
    """Uygulama ayarları penceresi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.setWindowTitle(translation_manager.tr("Settings"))
        self.setModal(True)
        self.setFixedSize(650, 700)  # Genişletildi
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Ayarlar arayüzünü oluştur"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # İndirme ayarları sekmesi
        download_tab = self.create_download_tab()
        self.tab_widget.addTab(download_tab, translation_manager.tr("Download"))
        
        # Uygulama ayarları sekmesi
        app_tab = self.create_app_tab()
        self.tab_widget.addTab(app_tab, translation_manager.tr("Application"))
        
        main_layout.addWidget(self.tab_widget)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        self.save_button = QPushButton(translation_manager.tr("Save"))
        self.save_button.setIcon(icon_manager.get_icon("save", "#FFFFFF"))
        style_manager.apply_button_style(self.save_button, "primary")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton(translation_manager.tr("Cancel"))
        self.cancel_button.setIcon(icon_manager.get_icon("x", "#FFFFFF"))
        style_manager.apply_button_style(self.cancel_button, "secondary")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def create_download_tab(self):
        """İndirme ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Ses kalitesi
        quality_group = self.create_group_box(translation_manager.tr("Audio Settings"))
        quality_layout = QVBoxLayout()
        quality_layout.setSpacing(10)
        quality_layout.setContentsMargins(10, 10, 10, 10)
        
        quality_row = QHBoxLayout()
        quality_label = QLabel(translation_manager.tr("Audio Quality:"))
        quality_label.setFixedWidth(150)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128 kbps", "192 kbps", "320 kbps"])
        quality_row.addWidget(quality_label)
        quality_row.addWidget(self.quality_combo)
        quality_row.addStretch()
        
        quality_layout.addLayout(quality_row)
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)
        
        # İndirme klasörü
        folder_group = self.create_group_box(translation_manager.tr("Download Location"))
        folder_layout = QVBoxLayout()
        folder_layout.setSpacing(10)
        folder_layout.setContentsMargins(10, 10, 10, 10)
        
        folder_row = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_button = QPushButton(translation_manager.tr("Browse..."))
        self.folder_button.setIcon(icon_manager.get_icon("folder", "#666666"))
        # Icon button için sabit boyut gerekli
        self.folder_button.setFixedSize(80, 32)
        self.folder_button.clicked.connect(self.browse_folder)
        
        folder_row.addWidget(self.folder_edit)
        folder_row.addWidget(self.folder_button)
        
        folder_layout.addLayout(folder_row)
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Performans ayarları
        perf_group = self.create_group_box(translation_manager.tr("Performance"))
        perf_layout = QVBoxLayout()
        perf_layout.setSpacing(15)  # Arttırıldı
        perf_layout.setContentsMargins(15, 20, 15, 15)  # Arttırıldı
        
        # Eşzamanlı indirme
        concurrent_row = self.create_spinbox_row(
            translation_manager.tr("Concurrent Downloads:"),
            self.create_spinbox(1, 5, 1)
        )
        self.concurrent_spin = concurrent_row.itemAt(1).widget()
        perf_layout.addLayout(concurrent_row)
        
        # Playlist limiti
        playlist_row = self.create_spinbox_row(
            translation_manager.tr("Playlist Limit:"),
            self.create_spinbox(0, 1000, 1, translation_manager.tr("Unlimited"))
        )
        self.playlist_spin = playlist_row.itemAt(1).widget()
        perf_layout.addLayout(playlist_row)
        
        # Cache limiti
        cache_row = self.create_spinbox_row(
            translation_manager.tr("URL Cache Limit:"),
            self.create_spinbox(100, 2000, 100, suffix=" URL")
        )
        self.cache_spin = cache_row.itemAt(1).widget()
        self.cache_spin.setToolTip(translation_manager.tr("Maximum cache size for URL checking"))
        perf_layout.addLayout(cache_row)
        
        # Otomatik yeniden deneme
        self.auto_retry_check = QCheckBox(translation_manager.tr("Automatically retry failed downloads"))
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Görünüm ayarları
        appearance_group = self.create_group_box(translation_manager.tr("Appearance"))
        appearance_layout = QVBoxLayout()
        appearance_layout.setSpacing(10)
        
        # Tema
        theme_row = QHBoxLayout()
        theme_label = QLabel(translation_manager.tr("Theme:"))
        theme_label.setFixedWidth(150)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([translation_manager.tr("Light"), translation_manager.tr("Dark")])
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        
        appearance_layout.addLayout(theme_row)
        
        # Dil seçimi
        language_row = QHBoxLayout()
        language_label = QLabel(translation_manager.tr("Language:"))
        language_label.setFixedWidth(150)
        self.language_combo = QComboBox()
        
        # Get available languages from translation manager
        languages = translation_manager.get_available_languages(native=True)
        
        # Add languages to combo box
        for code, name, flag in languages:
            display_text = f"{flag} {name}" if flag else name
            self.language_combo.addItem(display_text, code)
        
        # Set current language
        current_lang = self.config.get('language', 'tr')
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
        
        language_row.addWidget(language_label)
        language_row.addWidget(self.language_combo)
        language_row.addStretch()
        
        appearance_layout.addLayout(language_row)
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Bildirim ayarları
        notif_group = self.create_group_box(translation_manager.tr("Notifications"))
        notif_layout = QVBoxLayout()
        notif_layout.setSpacing(10)
        
        self.notif_sound_check = QCheckBox(translation_manager.tr("Play sound when download completes"))
        notif_layout.addWidget(self.notif_sound_check)
        
        self.auto_open_check = QCheckBox(translation_manager.tr("Automatically open folder after download"))
        notif_layout.addWidget(self.auto_open_check)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Geçmiş ayarları
        history_group = self.create_group_box(translation_manager.tr("Download History"))
        history_layout = QVBoxLayout()
        history_layout.setSpacing(10)
        
        history_row = QHBoxLayout()
        history_label = QLabel(translation_manager.tr("Keep history:"))
        history_label.setFixedWidth(150)
        self.history_combo = QComboBox()
        self.history_combo.addItems([translation_manager.tr("30 days"), translation_manager.tr("60 days"), translation_manager.tr("90 days"), translation_manager.tr("Forever")])
        history_row.addWidget(history_label)
        history_row.addWidget(self.history_combo)
        history_row.addStretch()
        
        history_layout.addLayout(history_row)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_group_box(self, title):
        """Styled group box oluştur"""
        group = QGroupBox(title)
        return group
    
    def create_spinbox(self, minimum, maximum, step=1, special_text=None, suffix=None):
        """Styled spinbox oluştur"""
        spinbox = QSpinBox()
        spinbox.setMinimum(minimum)
        spinbox.setMaximum(maximum)
        spinbox.setSingleStep(step)
        spinbox.setFixedWidth(120)  # Genişletildi
        spinbox.setFixedHeight(30)  # Sabit yükseklik
        
        if special_text:
            spinbox.setSpecialValueText(special_text)
        if suffix:
            spinbox.setSuffix(suffix)
            
        return spinbox
    
    def create_spinbox_row(self, label_text, spinbox):
        """Label ve spinbox içeren satır oluştur"""
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(150)
        row.addWidget(label)
        row.addWidget(spinbox)
        row.addStretch()
        return row
    
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
        self.cache_spin.setValue(self.config.get('max_cache_size', 500))
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
        self.config.set('max_cache_size', self.cache_spin.value())
        self.config.set('auto_retry', self.auto_retry_check.isChecked())
        
        # Uygulama ayarları
        theme = 'light' if self.theme_combo.currentIndex() == 0 else 'dark'
        self.config.set('theme', theme)
        
        # Dil ayarını kontrol et (henüz kaydetme)
        selected_language = self.language_combo.currentData()
        current_language = self.config.get('language', 'tr')
        
        self.config.set('notification_sound', self.notif_sound_check.isChecked())
        self.config.set('auto_open_folder', self.auto_open_check.isChecked())
        
        history_map = {0: 30, 1: 60, 2: 90, 3: 0}
        self.config.set('history_days', history_map[self.history_combo.currentIndex()])
        
        # Dil değiştiyse dinamik olarak güncelle
        if selected_language != current_language:
            # Dinamik olarak dili değiştir
            success = translation_manager.load_language(selected_language)
            
            if success:
                # Ana pencereyi güncelle
                if self.parent():
                    # Ana pencerede retranslateUi varsa çağır
                    if hasattr(self.parent(), 'retranslateUi'):
                        self.parent().retranslateUi()
                    # Tab widget'ları güncelle
                    if hasattr(self.parent(), 'tab_widget'):
                        # Tab başlıklarını güncelle
                        self.parent().tab_widget.setTabText(0, translation_manager.tr("İndir"))
                        self.parent().tab_widget.setTabText(1, translation_manager.tr("Geçmiş"))
                        self.parent().tab_widget.setTabText(2, translation_manager.tr("Sıra"))
                        self.parent().tab_widget.setTabText(3, translation_manager.tr("Dönüştür"))
                        
                        # Her tab'ın retranslateUi metodunu çağır
                        for i in range(self.parent().tab_widget.count()):
                            widget = self.parent().tab_widget.widget(i)
                            if hasattr(widget, 'retranslateUi'):
                                widget.retranslateUi()
                
                # Settings dialog'u da güncelle
                self.retranslateUi()
                
                # Dili config'e kaydet
                self.config.set('language', selected_language)
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    translation_manager.tr("Hata"),
                    translation_manager.tr("Dil değiştirilemedi. Lütfen uygulamayı yeniden başlatın.")
                )
        else:
            # Dil değişmemişse sadece kaydet
            self.config.set('language', selected_language)
        
        self.accept()
    
    def retranslateUi(self):
        """UI metinlerini yeniden çevir"""
        self.setWindowTitle(translation_manager.tr("Settings"))
        
        # Tab başlıkları
        self.tab_widget.setTabText(0, translation_manager.tr("Download"))
        self.tab_widget.setTabText(1, translation_manager.tr("Application"))
        
        # Butonlar
        self.save_button.setText(translation_manager.tr("Save"))
        self.cancel_button.setText(translation_manager.tr("Cancel"))