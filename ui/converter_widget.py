"""
MP3 Dönüştürücü Widget
Herhangi bir dosya türünü (video/ses) MP3'e dönüştürür
"""

import os
import subprocess
from pathlib import Path
import shutil
import static_ffmpeg
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QListWidget, QListWidgetItem,
                           QProgressBar, QMessageBox, QGroupBox,
                           QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor


class DragDropListWidget(QListWidget):
    """Sürükle-bırak destekli özel QListWidget"""
    
    files_dropped = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Sürükleme başladığında"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        """Sürükleme devam ederken"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event: QDropEvent):
        """Dosyalar bırakıldığında"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            files = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if Path(file_path).is_file():
                    files.append(file_path)
            if files:
                self.files_dropped.emit(files)
        else:
            event.ignore()


class ConversionWorker(QThread):
    """Dönüştürme işlemini yapan worker thread"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    file_completed = pyqtSignal(str, str, bool)  # input_path, output_path, is_replaced
    error = pyqtSignal(str)
    
    # Müzik dosyası uzantıları (bunlar yerinde değiştirilecek)
    AUDIO_EXTENSIONS = {'.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac', '.opus', 
                       '.aiff', '.ape', '.wv', '.dsf', '.dff'}
    
    # Video ve diğer medya uzantıları (bunlar yanına MP3 oluşturulacak)
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                       '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv', '.vob', '.ts', '.m2ts'}
    
    def __init__(self, files, replace_originals=True, ffmpeg_path='ffmpeg'):
        super().__init__()
        self.files = files
        self.bitrate = "320k"  # Maksimum kalite
        self.replace_originals = replace_originals
        self.is_running = True
        self.current_process = None
        self.ffmpeg_path = ffmpeg_path
        
    def run(self):
        """Dönüştürme işlemini başlat"""
        total_files = len(self.files)
        
        for index, file_path in enumerate(self.files):
            if not self.is_running:
                break
                
            try:
                input_file = Path(file_path)
                file_ext = input_file.suffix.lower()
                
                # Çıktı dosyasını belirle - her zaman aynı yerde MP3 oluştur
                output_file = input_file.with_suffix('.mp3')
                
                # Durum güncelle
                self.status.emit(self.tr("Dönüştürülüyor: {}").format(input_file.name))
                
                # FFmpeg komutu
                cmd = [
                    self.ffmpeg_path,
                    "-i", str(input_file),
                    "-vn",  # Video stream'i yok say
                    "-acodec", "libmp3lame",
                    "-ab", self.bitrate,
                    "-ar", "44100",  # Sample rate
                    "-y",  # Üzerine yaz
                    str(output_file)
                ]
                
                # FFmpeg'i çalıştır
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,  # stdout kullanılmıyor, buffer dolmasını önle
                    stderr=subprocess.PIPE
                )
                
                # İşlem tamamlanana kadar bekle (byte olarak al)
                stdout_bytes, stderr_bytes = self.current_process.communicate()
                process = self.current_process
                self.current_process = None
                
                # Decode stderr - errors='replace' ile geçersiz karakterler görünür kalır
                stderr = stderr_bytes.decode('utf-8', errors='replace')
                
                if process.returncode == 0:
                    # Başarılı - orijinal dosyayı sil (eğer ses dosyasıysa ve replace_originals true ise)
                    is_replaced = False
                    if file_ext in self.AUDIO_EXTENSIONS and self.replace_originals:
                        try:
                            input_file.unlink()
                            is_replaced = True
                        except OSError as e:
                            self.error.emit(self.tr("Orijinal dosya silinemedi ({}): {}").format(input_file.name, str(e)))
                    
                    self.file_completed.emit(str(input_file), str(output_file), is_replaced)
                else:
                    # Log the technical error for debugging (if needed)
                    if stderr.strip():
                        print(f"FFmpeg error for {input_file.name}: {stderr}")
                    
                    self.error.emit(self.tr("Hata ({}): Dosya dönüştürülemedi. Lütfen dosyanın bozuk olmadığını veya desteklenen bir formatta olduğunu kontrol edin.").format(input_file.name))
                
                # İlerleme güncelle
                progress = int((index + 1) / total_files * 100)
                self.progress.emit(progress)
                
            except (subprocess.SubprocessError, OSError, ValueError) as e:
                self.error.emit(self.tr("Dönüştürme hatası: {}").format(str(e)))
                
        self.status.emit(self.tr("Dönüştürme tamamlandı!") if self.is_running else self.tr("İptal edildi"))
        
    def stop(self):
        """Dönüştürmeyi durdur"""
        self.is_running = False
        # Eğer aktif bir FFmpeg process varsa sonlandır
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                # Process'in kapanmasını bekle (max 5 saniye)
                try:
                    self.current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Hala çalışıyorsa zorla kapat
                    self.current_process.kill()
                    self.current_process.wait()
            except (subprocess.SubprocessError, OSError) as e:
                self.error.emit(self.tr("FFmpeg process sonlandırılamadı: {}").format(str(e)))


class ConverterWidget(QWidget):
    """MP3 dönüştürücü ana widget"""
    
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = None
        self.setup_ffmpeg()
        self.init_ui()
        self.conversion_worker = None
        self.selected_files = set()
        self.file_items = {}  # Dict for O(1) lookup: {file_path: QListWidgetItem}
    
    def setup_ffmpeg(self):
        """FFmpeg kurulumunu kontrol et ve yükle"""
        try:
            # Önce static-ffmpeg'i dene
            static_ffmpeg.add_paths()
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                self.ffmpeg_path = ffmpeg_path
                return
        except Exception:
            pass
        
        # Sistem FFmpeg'ini kontrol et
        self.ffmpeg_path = shutil.which('ffmpeg')
        if not self.ffmpeg_path:
            QMessageBox.warning(
                None,
                self.tr("FFmpeg Bulunamadı"),
                self.tr("FFmpeg bulunamadı. MP3 dönüştürme özelliği devre dışı.\n\n"
                       "Lütfen FFmpeg'i yükleyin veya uygulamayı yeniden başlatın.")
            )
        
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Widget'lar arası genel boşluk
        
        # Başlık
        title = QLabel(self.tr("Her Türlü Dosyayı MP3'e Dönüştür"))
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Açıklama
        desc = QLabel(self.tr("Video, ses ve diğer medya dosyalarınızı MP3 formatına dönüştürün. "
                     "Dosyaları sürükleyip bırakabilir veya seçebilirsiniz."))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 0 10px 10px 10px;")
        layout.addWidget(desc)
        
        
        # Dosya seçme butonu
        select_btn = QPushButton(self.tr("Dosya Seç"))
        select_btn.clicked.connect(self.select_files)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(select_btn)
        
        # Dosya listesi
        self.file_list = DragDropListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px;
            }
            QListWidget:hover {
                border-color: #999;
                background-color: #f5f5f5;
            }
        """)
        self.file_list.files_dropped.connect(self.add_files)
        
        layout.addWidget(self.file_list)
        
        # Ayarlar grubu (başlıksız)
        settings_group = QGroupBox()
        settings_group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 10px;
                margin-bottom: 10px;
            }
        """)
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(10, 5, 10, 5)  # İçerik kenar boşlukları
        settings_layout.setSpacing(5)  # Widget'lar arası boşluk
        
        # Orijinal dosyaları silme seçeneği
        self.replace_checkbox = QCheckBox(self.tr("Ses dosyalarının orijinallerini sil"))
        self.replace_checkbox.setChecked(True)
        self.replace_checkbox.setToolTip(self.tr("İşaretli ise, ses dosyaları MP3'e dönüştürüldükten sonra silinir. "
                                        "Video dosyaları her zaman korunur."))
        self.replace_checkbox.stateChanged.connect(self.on_replace_checkbox_changed)
        settings_layout.addWidget(self.replace_checkbox)
        
        # Uyarı mesajı - checkbox'un hemen altında
        self.warning_label = QLabel(self.tr("DİKKAT: Ses dosyaları (WAV, FLAC, M4A vb.) MP3'e dönüştürüldükten sonra "
                                   "orijinal dosyalar otomatik olarak silinir. Video dosyaları korunur."))
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                color: #856404;
                padding: 8px;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                margin-top: 5px;
            }
        """)
        settings_layout.addWidget(self.warning_label)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Durum etiketi
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Buton layout'u için margin kaldır
        
        self.convert_btn = QPushButton(self.tr("Dönüştürmeyi Başlat"))
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        
        # FFmpeg yoksa butonu devre dışı bırak
        if not self.ffmpeg_path:
            self.convert_btn.setToolTip(self.tr("FFmpeg bulunamadı. Dönüştürme özelliği kullanılamaz."))
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        button_layout.addWidget(self.convert_btn)
        
        self.cancel_btn = QPushButton(self.tr("İptal Et"))
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        self.clear_btn = QPushButton(self.tr("Listeyi Temizle"))
        self.clear_btn.clicked.connect(self.clear_list)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def on_replace_checkbox_changed(self, state):
        """Checkbox durumu değiştiğinde"""
        # Checkbox işaretli ise uyarıyı göster, değilse gizle
        self.warning_label.setVisible(self.replace_checkbox.isChecked())
        
        # Listedeki ses dosyalarının açıklamalarını güncelle
        for file_path, item in self.file_items.items():
            file_ext = Path(file_path).suffix.lower()
            file_name = os.path.basename(file_path)
            
            # Sadece ses dosyalarını güncelle ve henüz dönüştürülmemiş olanları
            if file_ext in ConversionWorker.AUDIO_EXTENSIONS and not item.text().startswith("✓"):
                if self.replace_checkbox.isChecked():
                    item.setText("🎵 {} ({})".format(file_name, self.tr("Orijinal silinecek")))
                else:
                    item.setText("🎵 {}".format(file_name))
        
    def select_files(self):
        """Dosya seçme dialogu"""
        # Desteklenen formatları dinamik olarak oluştur
        audio_exts = ' '.join([f'*{ext}' for ext in ConversionWorker.AUDIO_EXTENSIONS])
        video_exts = ' '.join([f'*{ext}' for ext in ConversionWorker.VIDEO_EXTENSIONS])
        all_exts = f"{audio_exts} {video_exts}"
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Dönüştürülecek Dosyaları Seç"),
            "",
            self.tr("Desteklenen Dosyalar ({});;Video Dosyaları ({});;Ses Dosyaları ({});;Tüm Dosyalar (*.*)").format(all_exts, video_exts, audio_exts)
        )
        
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        """Dosyaları listeye ekle"""
        
        for file_path in files:
            # MP3 dosyalarını ekleme
            if file_path.lower().endswith('.mp3'):
                self.status_label.setText(self.tr("{} zaten MP3 formatında!").format(os.path.basename(file_path)))
                self.status_label.setStyleSheet("color: orange; padding: 5px;")
                continue
                
            # Zaten listede var mı kontrol et
            if file_path not in self.selected_files:
                self.selected_files.add(file_path)
                
                # Dosya tipine göre ikon ve bilgi ekle
                file_ext = Path(file_path).suffix.lower()
                file_name = os.path.basename(file_path)
                
                if file_ext in ConversionWorker.AUDIO_EXTENSIONS:
                    if self.replace_checkbox.isChecked():
                        display_text = "🎵 {} ({})".format(file_name, self.tr("Orijinal silinecek"))
                    else:
                        display_text = "🎵 {}".format(file_name)
                elif file_ext in ConversionWorker.VIDEO_EXTENSIONS:
                    display_text = "🎬 {}".format(file_name)
                else:
                    display_text = "📄 {}".format(file_name)
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, file_path)
                self.file_list.addItem(item)
                self.file_items[file_path] = item  # Store for O(1) lookup
                
        # Dönüştür butonunu aktif et (FFmpeg varsa)
        if self.selected_files and self.ffmpeg_path:
            self.convert_btn.setEnabled(True)
            self.status_label.setText(self.tr("{} dosya seçildi").format(len(self.selected_files)))
            self.status_label.setStyleSheet("color: green; padding: 5px;")
        elif self.selected_files and not self.ffmpeg_path:
            self.status_label.setText(self.tr("FFmpeg bulunamadı - Dönüştürme yapılamaz"))
            self.status_label.setStyleSheet("color: red; padding: 5px;")
            
    def clear_list(self):
        """Listeyi temizle"""
        self.file_list.clear()
        self.selected_files.clear()
        self.file_items.clear()  # Clear the lookup dict
        self.convert_btn.setEnabled(False)
        self.status_label.setText("")
        
    def start_conversion(self):
        """Dönüştürme işlemini başlat"""
        if not self.selected_files:
            return
        
        # UI'yi güncelle
        self.convert_btn.setEnabled(False)
        self.convert_btn.setVisible(False)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setVisible(True)
        self.clear_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Worker thread'i başlat
        self.conversion_worker = ConversionWorker(
            list(self.selected_files),  # Set'i liste'ye çevir
            self.replace_checkbox.isChecked(),
            self.ffmpeg_path or 'ffmpeg'  # FFmpeg yolu veya varsayılan
        )
        
        # Sinyalleri bağla
        self.conversion_worker.progress.connect(self.update_progress)
        self.conversion_worker.status.connect(self.update_status)
        self.conversion_worker.file_completed.connect(self.file_completed)
        self.conversion_worker.error.connect(self.show_error)
        self.conversion_worker.finished.connect(self.conversion_finished)
        
        # Başlat
        self.conversion_worker.start()
        
    def update_progress(self, value):
        """İlerleme güncelle"""
        self.progress_bar.setValue(value)
        
    def update_status(self, status):
        """Durum güncelle"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet("color: #2196F3; padding: 5px;")
        
    def file_completed(self, input_path, output_path, is_replaced):
        """Dosya tamamlandığında"""
        # O(1) lookup ile hızlı bul
        if input_path in self.file_items:
            item = self.file_items[input_path]
            current_text = item.text()
            if is_replaced:
                item.setText("✓ {} → MP3 ({})".format(current_text, self.tr("Orijinal silindi")))
            else:
                item.setText("✓ {} → MP3".format(current_text))
            item.setForeground(QColor("green"))
                
    def show_error(self, error):
        """Hata göster"""
        QMessageBox.warning(self, self.tr("Hata"), error)
        
    def cancel_conversion(self):
        """Dönüştürme işlemini iptal et"""
        if self.conversion_worker:
            self.conversion_worker.stop()
            self.status_label.setText(self.tr("İptal ediliyor..."))
            self.status_label.setStyleSheet("color: orange; padding: 5px;")
    
    def conversion_finished(self):
        """Dönüştürme tamamlandığında"""
        self.convert_btn.setEnabled(True)
        self.convert_btn.setVisible(True)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setVisible(False)
        self.clear_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if self.conversion_worker and self.conversion_worker.is_running:
            QMessageBox.information(
                self,
                self.tr("Tamamlandı"),
                self.tr("Tüm dosyalar başarıyla MP3'e dönüştürüldü!")
            )
            
        self.conversion_worker = None
