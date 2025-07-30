import os
import threading
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                            QProgressBar, QMessageBox, QMenuBar, QMenu,
                            QAction, QTabWidget, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QDesktopServices, QColor
from PyQt5.QtCore import QUrl
from core.downloader import Downloader, DownloadSignals
from ui.settings_dialog import SettingsDialog
from ui.history_widget import HistoryWidget
from ui.queue_widget import QueueWidget
from utils.config import Config


class MP3YapMainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Yap - YouTube İndirici")
        self.setGeometry(100, 100, 800, 600)
        
        # Pencereye gölge efekti ekle
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        # Config
        self.config = Config()
        
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
        
        # Menü çubuğu
        self.setup_menu()
        
        # Arayüz kurulumu
        self.setup_ui()
        
        # Sinyal bağlantıları (UI kurulumundan sonra)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.download_finished)
        self.signals.error.connect(self.download_error)
        self.signals.status_update.connect(self.update_status)
    
    def setup_menu(self):
        """Menü çubuğunu oluştur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')
        
        # URL'leri içe aktar
        import_action = QAction('URL\'leri İçe Aktar...', self)
        import_action.setShortcut('Ctrl+I')
        import_action.triggered.connect(self.import_urls)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Çıkış
        exit_action = QAction('Çıkış', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Ayarlar menüsü
        settings_menu = menubar.addMenu('Ayarlar')
        
        # Tercihler
        pref_action = QAction('Tercihler...', self)
        pref_action.setShortcut('Ctrl+,')
        pref_action.triggered.connect(self.show_settings)
        settings_menu.addAction(pref_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('Yardım')
        
        # Hakkında
        about_action = QAction('Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana widget olarak tab widget kullan
        self.tab_widget = QTabWidget()
        
        # İndirme sekmesi
        download_tab = self.create_download_tab()
        self.tab_widget.addTab(download_tab, "İndirme")
        
        # Geçmiş sekmesi
        self.history_widget = HistoryWidget()
        self.history_widget.redownload_signal.connect(self.add_url_to_download)
        self.tab_widget.addTab(self.history_widget, "Geçmiş")
        
        # Kuyruk sekmesi
        self.queue_widget = QueueWidget()
        self.queue_widget.start_download.connect(self.process_queue_item)
        self.tab_widget.addTab(self.queue_widget, "Kuyruk")
        
        # Ana widget olarak tab widget'ı ayarla
        self.setCentralWidget(self.tab_widget)
    
    def create_download_tab(self):
        """İndirme sekmesini oluştur"""
        widget = QWidget()
        layout = QVBoxLayout()
        
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
        self.download_button.setStyleSheet("""
            QPushButton {
                padding: 5px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # Kuyruğa ekle butonu
        self.add_to_queue_button = QPushButton("Kuyruğa Ekle")
        self.add_to_queue_button.clicked.connect(self.add_to_queue)  # type: ignore
        self.add_to_queue_button.setStyleSheet("""
            QPushButton {
                padding: 5px 20px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # Klasörü aç butonu
        self.open_folder_button = QPushButton("Klasörü Aç")
        self.open_folder_button.clicked.connect(self.open_output_folder)  # type: ignore
        self.open_folder_button.setEnabled(False)
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
            }
            QPushButton:disabled {
                color: #999;
            }
        """)
        
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.add_to_queue_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        
        # Layout'a widget'ları ekle
        layout.addWidget(url_label)
        layout.addWidget(self.url_text)
        layout.addLayout(status_layout)
        layout.addLayout(progress_layout)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
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
        output_path = self.config.get('output_path', 'music')
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
        
        def download_thread():
            self.downloader.download_all(urls, output_path)
            # İndirme bitince butonları etkinleştir
            self.download_button.setEnabled(True)
            self.open_folder_button.setEnabled(True)
            # Ayarlara göre klasörü aç
            if self.config.get('auto_open_folder', False):
                self.open_output_folder()
        
        thread = threading.Thread(target=download_thread)
        thread.start()
    
    def open_output_folder(self):
        """İndirilen dosyaların bulunduğu klasörü aç"""
        output_path = self.config.get('output_path', 'music')
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
            
        if os.path.exists(output_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        else:
            QMessageBox.information(self, "Bilgi", "Henüz hiç dosya indirilmemiş!")
    
    def show_settings(self):
        """Ayarlar penceresini göster"""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Ayarlar değişmiş olabilir, gerekli güncellemeleri yap
            pass
    
    def show_about(self):
        """Hakkında dialogunu göster"""
        QMessageBox.about(self, "MP3 Yap Hakkında",
            "<h3>MP3 Yap - YouTube İndirici</h3>"
            "<p>Sürüm 2.0</p>"
            "<p>YouTube videolarını MP3 formatında indirmek için modern ve kullanıcı dostu bir araç.</p>"
            "<p><b>Geliştirici:</b> Mehmet Yerli</p>"
            "<p><b>Web:</b> <a href='https://mehmetyerli.com'>mehmetyerli.com</a></p>"
            "<p><b>Lisans:</b> Açık Kaynak</p>")
    
    def import_urls(self):
        """URL'leri metin dosyasından içe aktar"""
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "URL Dosyası Seç", 
            "", 
            "Metin Dosyaları (*.txt);;Tüm Dosyalar (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    urls = f.read()
                    self.url_text.setPlainText(urls)
                    QMessageBox.information(self, "Başarılı", 
                        f"{len(urls.strip().split())} URL başarıyla yüklendi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya okunamadı: {str(e)}")
    
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
            # Geçmiş sekmesini güncelle
            if hasattr(self, 'history_widget'):
                self.history_widget.load_history()
    
    def add_url_to_download(self, url):
        """Geçmişten URL'yi indirme listesine ekle"""
        current_text = self.url_text.toPlainText().strip()
        if current_text:
            self.url_text.setPlainText(current_text + '\n' + url)
        else:
            self.url_text.setPlainText(url)
        # İndirme sekmesine geç
        self.tab_widget.setCurrentIndex(0)
        QMessageBox.information(self, "Başarılı", "URL indirme listesine eklendi!")
    
    def add_to_queue(self):
        """URL'leri kuyruğa ekle"""
        urls = self.url_text.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir URL girin!")
            return
        
        # URL'leri kuyruğa ekle
        added_count = 0
        for url in urls:
            try:
                self.queue_widget.add_to_queue(url)
                added_count += 1
            except Exception as e:
                print(f"URL eklenirken hata: {e}")
        
        if added_count > 0:
            QMessageBox.information(self, "Başarılı", 
                                  f"{added_count} URL kuyruğa eklendi!")
            self.url_text.clear()
            # Kuyruk sekmesine geç
            self.tab_widget.setCurrentIndex(2)
    
    def process_queue_item(self, queue_item):
        """Kuyruktan gelen öğeyi işle"""
        # İndirme durumunu güncelle
        self.queue_widget.update_download_status(queue_item['id'], 'downloading')
        
        # Downloader'ı hazırla
        self.current_queue_item = queue_item
        
        # Sinyal bağlantılarını güncelle (kuyruk için)
        try:
            self.signals.finished.disconnect()
            self.signals.error.disconnect()
        except:
            pass
        
        self.signals.finished.connect(self.queue_download_finished)
        self.signals.error.connect(self.queue_download_error)
        
        # İndirmeyi başlat
        output_dir = self.config.get('output_directory', 'music')
        download_thread = threading.Thread(
            target=self.downloader.download_all,
            args=([queue_item['url']], output_dir)
        )
        download_thread.start()
    
    def queue_download_finished(self, filename):
        """Kuyruk indirmesi tamamlandığında"""
        if hasattr(self, 'current_queue_item'):
            self.queue_widget.update_download_status(
                self.current_queue_item['id'], 'completed'
            )
            # Geçmişi güncelle
            if hasattr(self, 'history_widget'):
                self.history_widget.load_history()
    
    def queue_download_error(self, filename, error):
        """Kuyruk indirmesinde hata oluştuğunda"""
        if hasattr(self, 'current_queue_item'):
            self.queue_widget.update_download_status(
                self.current_queue_item['id'], 'failed', error
            )
    
    def closeEvent(self, a0):
        """Pencere kapatılırken"""
        # Direkt kapat
        a0.accept()