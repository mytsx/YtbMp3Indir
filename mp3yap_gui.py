import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, QProgressBar, 
                            QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject
import yt_dlp

# Sinyal sınıfı - indirme ilerlemesini GUI'ye iletmek için
class DownloadSignals(QObject):
    progress = pyqtSignal(str, float, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str)
    status_update = pyqtSignal(str)

# İndirme işlemini yönetecek sınıf
class Downloader:
    def __init__(self, signals):
        self.signals = signals
        self.is_running = False
        self.current_url = None
    
    def download_progress_hook(self, d):
        """İndirme ilerlemesini takip eden fonksiyon"""
        if d['status'] == 'downloading':
            filename = os.path.basename(d['filename'])
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                self.signals.progress.emit(filename, percent, f"%{percent:.1f}")
            else:
                mb_downloaded = d['downloaded_bytes']/1024/1024
                self.signals.progress.emit(filename, -1, f"{mb_downloaded:.1f} MB")
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            self.signals.finished.emit(filename)
        elif d['status'] == 'error':
            filename = os.path.basename(d.get('filename', 'Bilinmeyen dosya'))
            self.signals.error.emit(filename, str(d.get('error', 'Bilinmeyen hata')))

    def process_url(self, url, output_path):
        """URL'yi işler ve MP3 olarak indirir"""
        self.current_url = url
        self.signals.status_update.emit(f"İndiriliyor: {url}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '44100',
                '-ac', '2',
            ],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'prefer_ffmpeg': True,
            'ignoreerrors': True,
            'noplaylist': False,  # Playlist'leri işlemeye izin ver
            'progress_hooks': [self.download_progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.signals.status_update.emit(f"İndirme tamamlandı: {url}")
            return True
        except yt_dlp.DownloadError as e:
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"İndirme hatası: {e}")
            return False
        except KeyboardInterrupt:
            self.signals.status_update.emit("İndirme kullanıcı tarafından durduruldu")
            return False
        except (OSError, IOError) as e:
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"Dosya sistem hatası: {e}")
            return False
        except Exception as e:  # pylint: disable=broad-except
            # Beklenmeyen hatalar için fallback
            self.signals.error.emit(url, str(e))
            self.signals.status_update.emit(f"Beklenmeyen hata: {e}")
            return False

    def download_all(self, urls, output_path):
        """Tüm URL'leri indir"""
        self.is_running = True
        
        # Çıktı dizinini oluştur
        os.makedirs(output_path, exist_ok=True)
        
        for i, url in enumerate(urls, 1):
            if not self.is_running:
                self.signals.status_update.emit("İndirme durduruldu")
                break
                
            self.signals.status_update.emit(f"URL {i}/{len(urls)} işleniyor")
            success = self.process_url(url, output_path)
            
            if not success and not self.is_running:
                break
        
        self.is_running = False
        self.signals.status_update.emit("Tüm indirmeler tamamlandı")

    def stop(self):
        """İndirmeyi durdur"""
        self.is_running = False


# Ana uygulama penceresi
class MP3YapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Yap - YouTube İndirici")
        self.setMinimumSize(600, 400)
        
        # Thread referansı
        self.download_thread = None
        
        # UI elementlerini önceden tanımla
        self.url_text: QTextEdit
        self.status_label: QLabel
        self.current_file_label: QLabel
        self.progress_bar: QProgressBar
        self.progress_percent: QLabel
        self.download_button: QPushButton
        
        # Sinyaller
        self.signals = DownloadSignals()
        self.downloader = Downloader(self.signals)
        
        # Instance attributes initialization
        self.url_text: QTextEdit
        self.status_label: QLabel
        self.current_file_label: QLabel
        self.progress_bar: QProgressBar
        self.progress_percent: QLabel
        self.download_button: QPushButton
        
        # Arayüz kurulumu
        self.setup_ui()
        
        # Sinyal bağlantıları (UI kurulumundan sonra)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.download_finished)
        self.signals.error.connect(self.download_error)
        self.signals.status_update.connect(self.update_status)
    
    def setup_ui(self):
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
        button_layout.addWidget(self.download_button)
        
        # Layout'ları ana layout'a ekle
        main_layout.addWidget(url_label)
        main_layout.addWidget(self.url_text)
        main_layout.addLayout(status_layout)
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(button_layout)
        
        # Ana widget'ı ayarla
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def start_download(self):
        # URL'leri al
        text = self.url_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir URL girin.")
            return
        
        # URL'leri satırlara ayır ve boş satırları filtrele
        urls = [url.strip() for url in text.split('\n') if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Uyarı", "Geçerli URL bulunamadı.")
            return
        
        # İndirme klasörünü ayarla
        # PyInstaller ile paketlenmiş uygulamalar için çalışacak şekilde yolu belirle
        if getattr(sys, 'frozen', False):
            # PyInstaller ile paketlenmiş
            application_path = os.path.dirname(sys.executable)
        else:
            # Normal Python betiği
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        output_dir = os.path.join(application_path, "music")
        
        # Klasörün oluşturulduğundan emin ol ve kullanıcıya bildir
        try:
            os.makedirs(output_dir, exist_ok=True)
            self.status_label.setText(f"İndirme klasörü: {output_dir}")
            QMessageBox.information(self, "Bilgi", f"İndirilen dosyalar şu klasöre kaydedilecek:\n{output_dir}")
        except PermissionError as e:
            QMessageBox.warning(self, "Hata", f"Klasör oluşturma izni yok: {e}")
            return
        except OSError as e:
            QMessageBox.warning(self, "Hata", f"İndirme klasörü oluşturulamadı: {e}")
            return
        
        # Butonları güncelle
        self.download_button.setEnabled(False)
        
        # İlerleme çubuğunu sıfırla
        self.progress_bar.setValue(0)
        self.current_file_label.setText("Dosya: ")
        self.progress_percent.setText("0%")
        
        # İndirme işlemini başlat
        self.download_thread = threading.Thread(
            target=self.downloader.download_all,
            args=(urls, output_dir)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def update_progress(self, filename, percent, text):
        self.current_file_label.setText(f"Dosya: {filename}")
        if percent >= 0:
            self.progress_bar.setValue(int(percent))
        self.progress_percent.setText(text)
    
    def download_finished(self, filename):
        self.status_label.setText(f"İndirme tamamlandı: {filename}")
    
    def download_error(self, filename, error):
        self.status_label.setText(f"Hata: {filename} - {error}")
    
    def update_status(self, status):
        self.status_label.setText(status)
        # Eğer tüm indirmeler tamamlandıysa butonları güncelle
        if status == "Tüm indirmeler tamamlandı" or status == "İndirme durduruldu":
            self.download_button.setEnabled(True)


# Uygulamayı başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3YapApp()
    window.show()
    sys.exit(app.exec_())
