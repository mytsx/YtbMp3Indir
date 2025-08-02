"""
MP3 Dönüştürücü Widget
Herhangi bir dosya türünü (video/ses) MP3'e dönüştürür
"""

import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QListWidget, QListWidgetItem,
                           QProgressBar, QMessageBox, QComboBox, QGroupBox,
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
                if os.path.isfile(file_path):
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
    
    def __init__(self, files, replace_originals=True):
        super().__init__()
        self.files = files
        self.bitrate = "320k"  # Maksimum kalite
        self.replace_originals = replace_originals
        self.is_running = True
        self.current_process = None
        
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
                self.status.emit(f"Dönüştürülüyor: {input_file.name}")
                
                # FFmpeg komutu
                cmd = [
                    "ffmpeg",
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
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                
                # İşlem tamamlanana kadar bekle
                stdout, stderr = self.current_process.communicate()
                process = self.current_process
                self.current_process = None
                
                if process.returncode == 0:
                    # Başarılı - orijinal dosyayı sil (eğer ses dosyasıysa ve replace_originals true ise)
                    is_replaced = False
                    if file_ext in self.AUDIO_EXTENSIONS and self.replace_originals:
                        try:
                            os.remove(str(input_file))
                            is_replaced = True
                        except OSError as e:
                            self.error.emit(f"Orijinal dosya silinemedi ({input_file.name}): {str(e)}")
                    
                    self.file_completed.emit(str(input_file), str(output_file), is_replaced)
                else:
                    self.error.emit(f"Hata ({input_file.name}): {stderr}")
                
                # İlerleme güncelle
                progress = int((index + 1) / total_files * 100)
                self.progress.emit(progress)
                
            except Exception as e:
                self.error.emit(f"Hata: {str(e)}")
                
        self.status.emit("Dönüştürme tamamlandı!" if self.is_running else "İptal edildi")
        
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
            except Exception as e:
                self.error.emit(f"FFmpeg process sonlandırılamadı: {str(e)}")


class ConverterWidget(QWidget):
    """MP3 dönüştürücü ana widget"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.conversion_worker = None
        self.selected_files = []
        
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Widget'lar arası genel boşluk
        
        # Başlık
        title = QLabel("Her Türlü Dosyayı MP3'e Dönüştür")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Açıklama
        desc = QLabel("Video, ses ve diğer medya dosyalarınızı MP3 formatına dönüştürün. "
                     "Dosyaları sürükleyip bırakabilir veya seçebilirsiniz.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 0 10px 10px 10px;")
        layout.addWidget(desc)
        
        
        # Dosya seçme butonu
        select_btn = QPushButton("Dosya Seç")
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
        self.replace_checkbox = QCheckBox("Ses dosyalarının orijinallerini sil")
        self.replace_checkbox.setChecked(True)
        self.replace_checkbox.setToolTip("İşaretli ise, ses dosyaları MP3'e dönüştürüldükten sonra silinir. "
                                        "Video dosyaları her zaman korunur.")
        self.replace_checkbox.stateChanged.connect(self.on_replace_checkbox_changed)
        settings_layout.addWidget(self.replace_checkbox)
        
        # Uyarı mesajı - checkbox'un hemen altında
        self.warning_label = QLabel("DİKKAT: Ses dosyaları (WAV, FLAC, M4A vb.) MP3'e dönüştürüldükten sonra "
                                   "orijinal dosyalar otomatik olarak silinir. Video dosyaları korunur.")
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
        
        self.convert_btn = QPushButton("Dönüştürmeyi Başlat")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
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
        
        self.cancel_btn = QPushButton("İptal Et")
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
        
        self.clear_btn = QPushButton("Listeyi Temizle")
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
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            if file_path:
                file_ext = Path(file_path).suffix.lower()
                file_name = os.path.basename(file_path)
                
                # Sadece ses dosyalarını güncelle ve henüz dönüştürülmemiş olanları
                if file_ext in ConversionWorker.AUDIO_EXTENSIONS and not item.text().startswith("✓"):
                    if self.replace_checkbox.isChecked():
                        item.setText(f"🎵 {file_name} (Orijinal silinecek)")
                    else:
                        item.setText(f"🎵 {file_name}")
        
    def select_files(self):
        """Dosya seçme dialogu"""
        # Desteklenen formatları dinamik olarak oluştur
        audio_exts = ' '.join([f'*{ext}' for ext in ConversionWorker.AUDIO_EXTENSIONS])
        video_exts = ' '.join([f'*{ext}' for ext in ConversionWorker.VIDEO_EXTENSIONS])
        all_exts = f"{audio_exts} {video_exts}"
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Dönüştürülecek Dosyaları Seç",
            "",
            f"Desteklenen Dosyalar ({all_exts});;Video Dosyaları ({video_exts});;Ses Dosyaları ({audio_exts});;Tüm Dosyalar (*.*)"
        )
        
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        """Dosyaları listeye ekle"""
        added_count = 0
        
        for file_path in files:
            # MP3 dosyalarını ekleme
            if file_path.lower().endswith('.mp3'):
                self.status_label.setText(f"{os.path.basename(file_path)} zaten MP3 formatında!")
                self.status_label.setStyleSheet("color: orange; padding: 5px;")
                continue
                
            # Zaten listede var mı kontrol et
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                
                # Dosya tipine göre ikon ve bilgi ekle
                file_ext = Path(file_path).suffix.lower()
                file_name = os.path.basename(file_path)
                
                if file_ext in ConversionWorker.AUDIO_EXTENSIONS:
                    if self.replace_checkbox.isChecked():
                        display_text = f"🎵 {file_name} (Orijinal silinecek)"
                    else:
                        display_text = f"🎵 {file_name}"
                elif file_ext in ConversionWorker.VIDEO_EXTENSIONS:
                    display_text = f"🎬 {file_name}"
                else:
                    display_text = f"📄 {file_name}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, file_path)
                self.file_list.addItem(item)
                added_count += 1
                
        # Dönüştür butonunu aktif et
        if self.selected_files:
            self.convert_btn.setEnabled(True)
            self.status_label.setText(f"{len(self.selected_files)} dosya seçildi")
            self.status_label.setStyleSheet("color: green; padding: 5px;")
            
    def clear_list(self):
        """Listeyi temizle"""
        self.file_list.clear()
        self.selected_files.clear()
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
            self.selected_files,
            self.replace_checkbox.isChecked()
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
        # Listede işaretle
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.data(Qt.UserRole) == input_path:
                current_text = item.text()
                if is_replaced:
                    item.setText(f"✓ {current_text} → MP3 (Orijinal silindi)")
                else:
                    item.setText(f"✓ {current_text} → MP3")
                item.setForeground(QColor("green"))
                break
                
    def show_error(self, error):
        """Hata göster"""
        QMessageBox.warning(self, "Hata", error)
        
    def cancel_conversion(self):
        """Dönüştürme işlemini iptal et"""
        if self.conversion_worker:
            self.conversion_worker.stop()
            self.status_label.setText("İptal ediliyor...")
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
                "Tamamlandı",
                "Tüm dosyalar başarıyla MP3'e dönüştürüldü!"
            )
            
        self.conversion_worker = None