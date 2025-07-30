import os
import threading
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                            QProgressBar, QMessageBox)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from core.downloader import Downloader, DownloadSignals


class MP3YapMainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Yap - YouTube İndirici")
        self.setGeometry(100, 100, 800, 600)
        
        # Instance attributes initialization
        self.url_text: QTextEdit
        self.status_label: QLabel
        self.current_file_label: QLabel
        self.progress_bar: QProgressBar
        self.progress_percent: QLabel
        self.download_button: QPushButton
        self.open_folder_button: QPushButton
        
        # Sinyaller ve downloader
        self.signals = DownloadSignals()
        self.downloader = Downloader(self.signals)
        
        # Arayüz kurulumu
        self.setup_ui()
        
        # Sinyal bağlantıları (UI kurulumundan sonra)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.download_finished)
        self.signals.error.connect(self.download_error)
        self.signals.status_update.connect(self.update_status)
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana widget ve layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # URL giriş alanı
        url_label = QLabel("İndirilecek YouTube URL'lerini buraya yapıştırın:")
        self.url_text = QTextEdit()
        
        # Durum ve ilerleme
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Hazır")
        status_layout.addWidget(self.status_label)
        
        # İndirme ilerleme çubuğu
        progress_layout = QHBoxLayout()
        self.current_file_label = QLabel("Dosya: ")
        self.progress_bar = QProgressBar()
        self.progress_percent = QLabel("0%")
        progress_layout.addWidget(self.current_file_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_percent)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.download_button = QPushButton("İndir")
        self.download_button.clicked.connect(self.start_download)  # type: ignore
        
        # Klasörü aç butonu (YENİ!)
        self.open_folder_button = QPushButton("📁 Klasörü Aç")
        self.open_folder_button.clicked.connect(self.open_output_folder)  # type: ignore
        self.open_folder_button.setEnabled(False)
        
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        
        # Layout'a widget'ları ekle
        main_layout.addWidget(url_label)
        main_layout.addWidget(self.url_text)
        main_layout.addLayout(status_layout)
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(button_layout)
        
        # Ana widget'ı ayarla
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def start_download(self):
        """İndirme işlemini başlat"""
        urls = self.url_text.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir URL girin!")
            return
        
        # Butonları devre dışı bırak
        self.download_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        
        # İndirme thread'ini başlat
        output_path = os.path.join(os.getcwd(), "music")
        
        def download_thread():
            self.downloader.download_all(urls, output_path)
            # İndirme bitince butonları etkinleştir
            self.download_button.setEnabled(True)
            self.open_folder_button.setEnabled(True)
        
        thread = threading.Thread(target=download_thread)
        thread.start()
    
    def open_output_folder(self):
        """İndirilen dosyaların bulunduğu klasörü aç"""
        output_path = os.path.join(os.getcwd(), "music")
        if os.path.exists(output_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        else:
            QMessageBox.information(self, "Bilgi", "Henüz hiç dosya indirilmemiş!")
    
    def update_progress(self, filename, percent, text):
        """İlerleme çubuğunu güncelle"""
        self.current_file_label.setText(f"Dosya: {filename}")
        if percent >= 0:
            self.progress_bar.setValue(int(percent))
        self.progress_percent.setText(text)
    
    def download_finished(self, filename):
        """İndirme tamamlandığında çağrılır"""
        self.status_label.setText(f"İndirme tamamlandı: {filename}")
    
    def download_error(self, filename, error):
        """İndirme hatası durumunda çağrılır"""
        self.status_label.setText(f"Hata: {filename} - {error}")
    
    def update_status(self, status):
        """Durum mesajını güncelle"""
        self.status_label.setText(status)
        # Eğer tüm indirmeler tamamlandıysa butonları güncelle
        if status == "🎉 Tüm indirmeler tamamlandı!" or status == "İndirme durduruldu":
            self.download_button.setEnabled(True)
            self.open_folder_button.setEnabled(True)