import os
import re
import threading
import yt_dlp
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                            QProgressBar, QMessageBox, QMenuBar, QMenu,
                            QAction, QTabWidget, QApplication)
from PyQt5.QtGui import QDesktopServices, QColor
from PyQt5.QtCore import QUrl, QTimer, QThread, pyqtSignal
from core.downloader import Downloader, DownloadSignals
from ui.settings_dialog import SettingsDialog
from ui.history_widget import HistoryWidget
from ui.queue_widget import QueueWidget
from utils.config import Config
from database.manager import DatabaseManager


class MP3YapMainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube MP3 İndirici")
        self.setGeometry(100, 100, 800, 600)
        
        # Gölge efektini kaldırdık - tablolarda sorun yaratıyor
        
        # Config ve Database
        self.config = Config()
        self.db_manager = DatabaseManager()
        
        # Instance attributes initialization
        self.url_text: QTextEdit
        self.status_label: QLabel
        self.current_file_label: QLabel
        self.progress_bar: QProgressBar
        self.progress_percent: QLabel
        self.download_button: QPushButton
        self.open_folder_button: QPushButton
        
        # URL kontrol cache
        self.url_cache = {}  # URL -> info dict
        self.last_checked_urls = set()  # Son kontrol edilen URL'ler
        
        # Sinyaller ve downloader
        self.signals = DownloadSignals()
        self.downloader = Downloader(self.signals)
        
        # Kuyruk için ayrı downloader
        self.queue_signals = DownloadSignals()
        self.queue_downloader = Downloader(self.queue_signals)
        
        # Menü çubuğu
        self.setup_menu()
        
        # Arayüz kurulumu
        self.setup_ui()
        
        # Sinyal bağlantıları (UI kurulumundan sonra)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.download_finished)
        self.signals.error.connect(self.download_error)
        self.signals.status_update.connect(self.update_status)
        
        # Kuyruk sinyalleri
        self.queue_signals.progress.connect(self.queue_download_progress)
        self.queue_signals.finished.connect(self.queue_download_finished)
        self.queue_signals.error.connect(self.queue_download_error)
        self.queue_signals.status_update.connect(self.queue_status_update)
    
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
        
        # Tab değişikliğini dinle
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
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
        self.status_label.setMinimumHeight(30)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
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
        self.download_button = QPushButton("▶ İndir")
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
        
        # İptal butonu
        self.cancel_button = QPushButton("⏹ İptal")
        self.cancel_button.clicked.connect(self.cancel_download)  # type: ignore
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                padding: 5px 20px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #da190b;
            }
            QPushButton:pressed:enabled {
                background-color: #ba000d;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # Kuyruğa ekle butonu
        self.add_to_queue_button = QPushButton("➕ Kuyruğa Ekle")
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
        
        # Temizle butonu
        self.clear_button = QPushButton("🗑 Temizle")
        self.clear_button.clicked.connect(self.clear_urls)  # type: ignore
        self.clear_button.setStyleSheet("""
            QPushButton {
                padding: 5px 20px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        
        # Klasörü aç butonu
        self.open_folder_button = QPushButton("📁 Klasörü Aç")
        self.open_folder_button.clicked.connect(self.open_output_folder)  # type: ignore
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                padding: 5px 20px;
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #7B1FA2;
            }
            QPushButton:pressed:enabled {
                background-color: #6A1B9A;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # Sol taraf - ana işlemler
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_to_queue_button)
        
        # Boşluk
        button_layout.addStretch()
        
        # Sağ taraf - yardımcı işlemler
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.open_folder_button)
        
        # URL durum çubuğu
        self.url_status_bar = QLabel("")
        self.url_status_bar.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        self.url_status_bar.setVisible(False)
        
        # Layout'a widget'ları ekle
        layout.addWidget(url_label)
        layout.addWidget(self.url_text)
        layout.addLayout(status_layout)
        layout.addLayout(progress_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.url_status_bar)
        
        # URL değişikliklerini dinle
        self.url_check_timer = QTimer()
        self.url_check_timer.setSingleShot(True)
        self.url_check_timer.timeout.connect(self.check_urls_delayed)
        self.url_text.textChanged.connect(self.on_url_text_changed)
        
        widget.setLayout(layout)
        return widget
    
    def start_download(self):
        """İndirme işlemini başlat"""
        urls = self.url_text.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir URL girin!")
            return
        
        # Butonları güncelle
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
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
        QMessageBox.about(self, "YouTube MP3 İndirici Hakkında",
            "<h3>YouTube MP3 İndirici</h3>"
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
        # Playlist progress varsa vurgula
        if '[' in text and '/' in text:
            # Playlist progress içeriyor
            self.current_file_label.setText(f"📋 Playlist İndiriliyor - Dosya: {filename}")
            self.progress_percent.setStyleSheet("""
                QLabel {
                    color: #1976D2;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        else:
            self.current_file_label.setText(f"Dosya: {filename}")
            self.progress_percent.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                }
            """)
            
        if percent >= 0:
            self.progress_bar.setValue(int(percent))
            self.progress_bar.setRange(0, 100)
        else:
            self.progress_bar.setRange(0, 0)  # Belirsiz ilerleme
        self.progress_percent.setText(text)
    
    def download_finished(self, filename):
        """İndirme tamamlandığında çağrılır"""
        self.status_label.setText(f"İndirme tamamlandı: {filename}")
    
    def download_error(self, filename, error):
        """İndirme hatası durumunda çağrılır"""
        self.status_label.setText(f"Hata: {filename} - {error}")
    
    def update_status(self, status):
        """Durum mesajını güncelle"""
        # Önemli uyarıları silme
        current_text = self.status_label.text()
        if any(x in current_text for x in ["UYARI:", "✅", "❌"]) and any(x in current_text.lower() for x in ["kuyrukta", "eklendi", "eklenemedi"]):
            # Kuyruk işlemi mesajı varsa üzerine yazma
            return
        self.status_label.setText(status)
        
        # Playlist progress'i de status bar'da göster
        if '[' in status and '/' in status and ']' in status:
            # Playlist progress içeriyor, bunu vurgula
            import re
            match = re.search(r'\[(\d+)/(\d+)\]', status)
            if match:
                current = match.group(1)
                total = match.group(2)
                # Status label'ı renklendir
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #1976D2;
                        font-weight: bold;
                        padding: 5px;
                        background-color: #E3F2FD;
                        border-radius: 3px;
                    }
                """)
        else:
            # Normal durum için stil sıfırla
            self.status_label.setStyleSheet("")
        
        # Eğer tüm indirmeler tamamlandıysa butonları güncelle
        if status == "🎉 Tüm indirmeler tamamlandı!" or status == "İndirme durduruldu":
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            # Geçmiş sekmesini güncelle
            if hasattr(self, 'history_widget'):
                self.history_widget.load_history()
            # İndirme tamamlandıysa URL'leri temizle
            if status == "🎉 Tüm indirmeler tamamlandı!":
                self.url_text.clear()
                self.url_status_bar.setVisible(False)
    
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
        
        # Loading göstergesi
        self.status_label.setText("🔄 Video bilgileri alınıyor...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #FFF3E0;
                color: #E65100;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        self.add_to_queue_button.setEnabled(False)
        self.download_button.setEnabled(False)
        QApplication.processEvents()  # UI güncelleme
        
        # yt-dlp seçenekleri
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'ignoreerrors': True,
            'skip_download': True,
        }
        
        # URL'leri kuyruğa ekle
        added_count = 0
        duplicate_videos = []  # Duplicate video listesi
        
        for url in urls:
            try:
                # Video başlığını al
                video_title = None
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            if info.get('_type') == 'playlist':
                                # Playlist ise her video için ayrı kayıt
                                playlist_title = info.get('title', 'İsimsiz Liste')
                                entries = info.get('entries', [])
                                for idx, entry in enumerate(entries):
                                    video_url = entry.get('url', '')
                                    video_title = entry.get('title', f'Video {idx+1}')
                                    full_title = f"[{playlist_title}] {video_title}"
                                    result = self.db_manager.add_to_queue(video_url, full_title)
                                    if result > 0:  # Başarılı
                                        added_count += 1
                                    elif result == -1:  # Duplicate
                                        duplicate_videos.append(video_title)
                            else:
                                # Tek video
                                video_title = info.get('title', 'İsimsiz Video')
                                result = self.db_manager.add_to_queue(url, video_title)
                                if result > 0:  # Başarılı
                                    added_count += 1
                                elif result == -1:  # Duplicate
                                    duplicate_videos.append(video_title)
                except Exception as e:
                    print(f"Video bilgisi alınamadı: {e}")
                    # Hata durumunda URL ile ekle
                    result = self.db_manager.add_to_queue(url, None)
                    if result > 0:
                        added_count += 1
                    elif result == -1:
                        duplicate_videos.append(url)
                    
            except Exception as e:
                print(f"URL eklenirken hata: {e}")
        
        # Butonları geri etkinleştir
        self.add_to_queue_button.setEnabled(True)
        self.download_button.setEnabled(True)
        self.status_label.setStyleSheet("")  # Stili sıfırla
        
        # Sonuç mesajı göster
        total_urls = len(urls)
        duplicate_count = total_urls - added_count
        
        if added_count > 0 and duplicate_count == 0:
            self.status_label.setText(f"✓ {added_count} video kuyruğa eklendi")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #E8F5E9;
                    color: #2E7D32;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            self.url_text.clear()  # URL'leri temizle
            # Kuyruğu yenile
            self.queue_widget.load_queue()
            # Kuyruk sekmesine geç
            self.tab_widget.setCurrentIndex(2)
        elif added_count > 0 and duplicate_count > 0:
            # Hem eklenen hem duplicate olanları göster
            if duplicate_count <= 2 and duplicate_videos:
                # Az sayıda duplicate varsa detay göster
                dup_names = ", ".join([v[:20] + "..." if len(v) > 20 else v for v in duplicate_videos[:2]])
                self.status_label.setText(f"✓ {added_count} eklendi | Kuyrukta: {dup_names}")
            else:
                self.status_label.setText(f"✓ {added_count} yeni eklendi | {duplicate_count} zaten kuyrukta")
            
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #FFF3E0;
                    color: #E65100;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            self.url_text.clear()
            # Kuyruğu yenile
            self.queue_widget.load_queue()
            self.tab_widget.setCurrentIndex(2)
        elif added_count == 0 and duplicate_count > 0:
            # Duplicate listesini göster
            if duplicate_videos and len(duplicate_videos) <= 3:
                # Az sayıda duplicate varsa isimleri göster
                video_names = ", ".join([v[:30] + "..." if len(v) > 30 else v for v in duplicate_videos[:3]])
                msg = f"Zaten kuyrukta: {video_names}"
            else:
                msg = f"Tüm videolar ({duplicate_count}) zaten kuyrukta"
            
            # Sadece status_label'da göster, popup açma
            self.status_label.setText(f"UYARI: {msg}")
            
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #FFEBEE;
                    color: #C62828;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            
            # URL'leri SİLME - kullanıcı ana ekranda indirmek isteyebilir
            # Sekme değiştirme YAPMA
            return  # Fonksiyondan çık
        else:
            self.status_label.setText("Hiçbir video eklenemedi")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #FFEBEE;
                    color: #C62828;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
    
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
            target=self.queue_downloader.download_all,
            args=([queue_item['url']], output_dir)
        )
        download_thread.start()
    
    def queue_download_progress(self, filename, percent, status):
        """Kuyruk indirme ilerlemesini güncelle"""
        # Kuyruk widget'ında ilerleme gösterebiliriz
        pass
    
    def queue_status_update(self, status):
        """Kuyruk durum güncellemesi"""
        if hasattr(self, 'current_queue_item') and self.current_queue_item:
            # Dönüştürme durumunu kontrol et
            if "MP3'e dönüştürülüyor" in status or "Dönüştürme" in status:
                self.queue_widget.update_download_status(
                    self.current_queue_item['id'], 'converting'
                )
    
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
    
    def on_tab_changed(self, index):
        """Tab değiştiğinde çağrılır"""
        # Geçmiş sekmesi (index 1) seçildiyse yenile
        if index == 1 and hasattr(self, 'history_widget'):
            self.history_widget.load_history()
    
    def cancel_download(self):
        """İndirmeyi iptal et"""
        # Downloader'ı durdur
        if hasattr(self, 'downloader'):
            self.downloader.stop()
        
        # Butonları güncelle
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_label.setText("İndirme iptal edildi")
            
    def clear_urls(self):
        """URL metin alanını temizle"""
        self.url_text.clear()
        self.status_label.setText("URL listesi temizlendi")
        self.url_status_bar.setVisible(False)
    
    def on_url_text_changed(self):
        """URL metni değiştiğinde"""
        # Eğer duplicate uyarısı varsa timer'ı başlatma
        current_text = self.status_label.text()
        if "kuyrukta" in current_text.lower() and "UYARI:" in current_text:
            return
            
        # Timer'ı durdur ve yeniden başlat (debounce)
        self.url_check_timer.stop()
        self.url_check_timer.start(500)  # 500ms bekle
    
    def check_urls_delayed(self):
        """Gecikmiş URL kontrolü"""
        # Kontrolü direkt çalıştır (QTimer zaten ana thread'de)
        self.check_urls()
    
    def check_urls(self):
        """URL'leri kontrol et ve durum göster"""
        urls = self.url_text.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            self.url_status_bar.setVisible(False)
            self.last_checked_urls.clear()
            return
        
        # Eğer aynı URL'ler zaten kontrol edildiyse cache'den göster
        current_urls = set(urls)
        if current_urls == self.last_checked_urls:
            self.show_cached_url_status(urls)
            return
        
        self.last_checked_urls = current_urls
        
        # Hemen loading göster
        self.url_status_bar.setText("⏳ URL'ler kontrol ediliyor...")
        self.url_status_bar.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #fff3e0;
                border: 1px solid #ff9800;
                border-radius: 4px;
                font-size: 12px;
                color: #e65100;
                font-weight: bold;
            }
        """)
        self.url_status_bar.setVisible(True)
        QApplication.processEvents()  # UI güncelle
        
        # Playlist URL'si varsa hemen kontrol başlat
        has_playlist = any('list=' in url for url in urls)
        if has_playlist:
            self.url_status_bar.setText("⏳ Playlist bilgisi alınıyor...")
            self.url_status_bar.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #1565c0;
                }
            """)
            self.url_status_bar.setVisible(True)
            QApplication.processEvents()  # UI güncelle
        
        # URL sayısını göster
        valid_urls = []
        invalid_urls = []
        
        # Regex ile hızlı YouTube URL kontrolü
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})'
        )
        
        for url in urls:
            # Önce regex ile hızlı kontrol
            match = youtube_regex.search(url)
            if match:
                # Video ID'yi al
                video_id = match.group(5)
                if video_id and len(video_id) == 11:
                    valid_urls.append(url)
                else:
                    # Video ID eksik veya hatalı
                    invalid_urls.append(url)
            else:
                # YouTube URL'si değil
                invalid_urls.append(url)
        
        # Liste URL'lerini kontrol et
        playlist_info = []
        
        # yt-dlp'yi dışarıda import et
        import yt_dlp
        
        for url in valid_urls:
            if 'list=' in url:
                # Bu bir playlist URL'si - detaylı bilgi al
                try:
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': 'in_playlist',  # Playlist metadata'sını al
                        'ignoreerrors': True,
                        'skip_download': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info and info.get('_type') == 'playlist':
                            # Playlist bilgisi
                            playlist_title = info.get('title', 'İsimsiz Liste')
                            playlist_size = info.get('playlist_count', 0)
                            if playlist_size == 0 and 'entries' in info:
                                playlist_size = len(info['entries'])
                            uploader = info.get('uploader', info.get('channel', ''))
                            
                            # Cache'e kaydet
                            self.url_cache[url] = {
                                'is_playlist': True,
                                'title': playlist_title,
                                'video_count': playlist_size,
                                'uploader': uploader
                            }
                            
                            playlist_info.append({
                                'url': url,
                                'title': playlist_title,
                                'count': playlist_size,
                                'uploader': uploader
                            })
                        else:
                            # Playlist URL'si gibi görünüyor ama değil
                            playlist_info.append({
                                'url': url,
                                'title': 'Tek Video',
                                'count': 1
                            })
                except Exception as e:
                    # Hata durumunda
                    print(f"Playlist bilgisi alınamadı: {e}")
                    playlist_info.append({
                        'url': url,
                        'title': 'Bilinmeyen',
                        'count': 1
                    })
            else:
                # Tek video
                if url not in self.url_cache:
                    # Cache'e ekle
                    self.url_cache[url] = {
                        'is_playlist': False,
                        'title': 'Tek Video',
                        'video_count': 1
                    }
                
                playlist_info.append({
                    'url': url,
                    'title': None,
                    'count': 1
                })
        
        # Durum mesajını oluştur
        status_parts = []
        
        # Geçerli URL sayısı ve playlist bilgisi
        if valid_urls:
            total_videos = sum(p['count'] for p in playlist_info)
            playlists = [p for p in playlist_info if p.get('count', 1) > 1]
            single_videos = [p for p in playlist_info if p.get('count', 1) == 1]
            
            # Detaylı bilgi
            if total_videos == len(valid_urls):
                # Sadece tek videolar var
                status_parts.append(f"✓ {len(valid_urls)} video indirmeye hazır")
            else:
                # Karışık (playlist + tek video)
                parts = []
                if playlists:
                    parts.append(f"{len(playlists)} playlist")
                if single_videos:
                    parts.append(f"{len(single_videos)} video")
                status_parts.append(f"✓ {' ve '.join(parts)} (toplam {total_videos} video)")
                
                # Playlist detayları
                for p in playlists:
                    if p.get('title') and p['title'] != 'Bilinmeyen':
                        playlist_text = f"  • {p['title'][:30]}"
                        if len(p['title']) > 30:
                            playlist_text += "..."
                        playlist_text += f" ({p['count']} video)"
                        status_parts.append(playlist_text)
        
        # Geçersiz URL sayısı
        invalid_count = len(invalid_urls)
        if invalid_count > 0:
            status_parts.append(f"✗ {invalid_count} geçersiz URL")
        
        # Veritabanında kontrol et
        already_downloaded = 0
        files_exist = 0
        files_missing = 0
        
        for url in valid_urls:
            # Veritabanında var mı kontrol et (tam eşleşme)
            existing = self.db_manager.get_download_by_url(url)
            if existing:
                already_downloaded += 1
                # En son indirilen kaydı kontrol et (birden fazla olabilir)
                latest_record = existing[0]  # En yeni kayıt
                
                # Dosya yolunu kontrol et
                file_found = False
                
                # file_path genellikle klasör yolu, file_name dosya adı
                if latest_record.get('file_path') and latest_record.get('file_name'):
                    # Tam dosya yolunu oluştur
                    full_file_path = os.path.join(latest_record['file_path'], latest_record['file_name'])
                    if os.path.exists(full_file_path):
                        file_found = True
                
                # Alternatif kontroller
                if not file_found and latest_record.get('file_name'):
                    # music klasöründe kontrol et
                    music_path = os.path.join('music', latest_record['file_name'])
                    if os.path.exists(music_path):
                        file_found = True
                    
                    # Absolute music path
                    abs_music_path = os.path.join(os.getcwd(), 'music', latest_record['file_name'])
                    if not file_found and os.path.exists(abs_music_path):
                        file_found = True
                
                if file_found:
                    files_exist += 1
                else:
                    files_missing += 1
        
        if files_exist > 0:
            status_parts.append(f"✓ {files_exist} dosya hem indirilmiş hem de klasörde mevcut")
        
        if files_missing > 0:
            status_parts.append(f"⚠ {files_missing} dosya daha önce indirilmiş ama klasörde bulunamadı")
        
        if already_downloaded > files_exist + files_missing:
            # Dosya yolu olmayan kayıtlar var
            unknown = already_downloaded - files_exist - files_missing
            status_parts.append(f"? {unknown} dosya kaydı eksik bilgi içeriyor")
        
        # Durum çubuğunu güncelle
        if status_parts:
            self.url_status_bar.setText(" | ".join(status_parts))
            self.url_status_bar.setVisible(True)
            
            # Renk ayarla - öncelik sırasına göre
            if invalid_count > 0:
                # Kırmızı - geçersiz URL var (en kritik)
                self.url_status_bar.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        background-color: #ffebee;
                        border: 1px solid #ef5350;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #c62828;
                        font-weight: bold;
                    }
                """)
            elif files_exist > 0 and files_missing == 0:
                # Mavi - tüm dosyalar mevcut (bilgilendirme)
                self.url_status_bar.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        background-color: #e3f2fd;
                        border: 1px solid #2196f3;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #1565c0;
                        font-weight: bold;
                    }
                """)
            elif files_missing > 0:
                # Sarı - dosyalar eksik (yeniden indirilebilir)
                self.url_status_bar.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        background-color: #fff3e0;
                        border: 1px solid #ff9800;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #e65100;
                        font-weight: bold;
                    }
                """)
            else:
                # Yeşil - yeni indirmeler için hazır
                self.url_status_bar.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        background-color: #e8f5e9;
                        border: 1px solid #4caf50;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #2e7d32;
                        font-weight: bold;
                    }
                """)
        else:
            self.url_status_bar.setVisible(False)
    
    def show_cached_url_status(self, urls):
        """Cache'den URL durumunu göster"""
        total_videos = 0
        playlists = []
        single_videos = []
        valid_urls = []
        invalid_count = 0
        
        # Regex ile hızlı YouTube URL kontrolü
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})'
        )
        
        for url in urls:
            if youtube_regex.search(url):
                valid_urls.append(url)
                # Cache'de var mı?
                if url in self.url_cache:
                    info = self.url_cache[url]
                    if info['is_playlist']:
                        playlists.append(info)
                        total_videos += info['video_count']
                    else:
                        single_videos.append(info)
                        total_videos += 1
                else:
                    # Cache'de yok, tek video varsay
                    single_videos.append({'title': 'Tek Video', 'video_count': 1})
                    total_videos += 1
            else:
                invalid_count += 1
        
        # Durum mesajını oluştur
        if total_videos == 0 and invalid_count == 0:
            self.url_status_bar.setVisible(False)
            return
            
        status_parts = []
        
        if total_videos > 0:
            if total_videos == len(valid_urls) and not playlists:
                # Sadece tek videolar var
                status_parts.append(f"✓ {len(valid_urls)} video indirmeye hazır")
            else:
                # Karışık (playlist + tek video)
                parts = []
                if playlists:
                    parts.append(f"{len(playlists)} playlist")
                if single_videos:
                    parts.append(f"{len(single_videos)} video")
                status_parts.append(f"✓ {' ve '.join(parts)} (toplam {total_videos} video) indirmeye hazır")
        
        if invalid_count > 0:
            status_parts.append(f"✗ {invalid_count} geçersiz URL")
        
        if status_parts:
            self.url_status_bar.setText(" | ".join(status_parts))
            # Renk ayarla
            if invalid_count > 0:
                # Kırmızı
                self.url_status_bar.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        background-color: #ffebee;
                        border: 1px solid #ef5350;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #c62828;
                        font-weight: bold;
                    }
                """)
            else:
                # Yeşil
                self.url_status_bar.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        background-color: #e8f5e9;
                        border: 1px solid #4caf50;
                        border-radius: 4px;
                        font-size: 12px;
                        color: #2e7d32;
                        font-weight: bold;
                    }
                """)
            self.url_status_bar.setVisible(True)
        else:
            self.url_status_bar.setVisible(False)
    
    def closeEvent(self, a0):
        """Pencere kapatılırken"""
        # Aktif indirme varsa durdur
        if hasattr(self, 'downloader') and self.downloader.is_running:
            self.downloader.stop()
        # Pencereyi kapat
        a0.accept()