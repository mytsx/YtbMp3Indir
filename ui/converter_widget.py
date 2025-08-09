"""
MP3 Dönüştürücü Widget
Herhangi bir dosya türünü (video/ses) MP3'e dönüştürür
"""

import html
import logging
import os
import shutil
import subprocess
import threading
from pathlib import Path

import static_ffmpeg
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor, QPainter, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QListWidget, QListWidgetItem,
                           QProgressBar, QMessageBox, QGroupBox,
                           QCheckBox, QGraphicsDropShadowEffect)
from styles import style_manager
from utils.icon_manager import icon_manager
from utils.translation_manager import translation_manager

# Configure logging
logger = logging.getLogger(__name__)



class DragDropListWidget(QListWidget):
    """Sürükle-bırak destekli özel QListWidget"""
    
    files_dropped = pyqtSignal(list)
    clicked_when_empty = pyqtSignal()  # Boş listeye tıklandığında sinyal
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        
    def mousePressEvent(self, event):
        """Liste'ye tıklandığında"""
        # Eğer liste boşsa ve tıklama olursa sinyal gönder
        if self.count() == 0:
            self.clicked_when_empty.emit()
        # Normal mouse press işlemini de yap
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        """Listeyi çiz - boşsa filigran ekle"""
        # Önce normal paint işlemini yap, sonra üzerine çiz.
        super().paintEvent(event)
        
        # Liste boşsa filigran metni göster
        if self.count() == 0:
            painter = QPainter(self.viewport())
            
            # Theme'e göre renk ayarla
            is_dark = style_manager.get_current_theme() == 'dark'
            
            if is_dark:
                # Koyu tema için açık gri
                painter.setPen(QColor(style_manager.colors.DARK_PLACEHOLDER_TEXT))
            else:
                # Açık tema için koyu gri
                painter.setPen(QColor(style_manager.colors.PLACEHOLDER_TEXT))
            
            # Font ayarları
            font = painter.font()
            font.setItalic(True)
            font.setPointSize(12)
            painter.setFont(font)
            
            # Metni ortala ve çiz
            text = translation_manager.tr("Drag and drop files to convert\nor click to select")
            rect = self.viewport().rect()
            painter.drawText(rect, Qt.AlignCenter, text)
            painter.end()
        
    def _handle_drag_event(self, event):
        """Handle drag events uniformly"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Sürükleme başladığında"""
        self._handle_drag_event(event)
            
    def dragMoveEvent(self, event):
        """Sürükleme devam ederken"""
        self._handle_drag_event(event)
            
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
    status = pyqtSignal(str, str)  # status_code, data (for translation in UI)
    file_completed = pyqtSignal(str, str, bool)  # input_path, output_path, is_replaced
    error = pyqtSignal(str, dict)  # error_code, data_dict (for translation in UI)
    
    # Constants
    BITRATE = "320k"  # Maximum quality MP3 bitrate
    
    # Müzik dosyası uzantıları (bunlar yerinde değiştirilecek)
    AUDIO_EXTENSIONS = {'.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac', '.opus', 
                       '.aiff', '.ape', '.wv', '.dsf', '.dff'}
    
    # Video ve diğer medya uzantıları (bunlar yanına MP3 oluşturulacak)
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                       '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv', '.vob', '.ts', '.m2ts'}
    
    def __init__(self, files, replace_originals=True, ffmpeg_path='ffmpeg'):
        super().__init__()
        self.files = files
        self.bitrate = self.BITRATE  # Maksimum kalite
        self.replace_originals = replace_originals
        self.is_running = True
        self.current_process = None
        self.process_lock = threading.Lock()  # Thread-safe access to current_process
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
                
                # Durum güncelle - send status code and data
                self.status.emit("converting", input_file.name)
                
                # FFmpeg komutu
                cmd = [
                    self.ffmpeg_path,
                    "-i", str(input_file),
                    "-vn",  # Video stream'i yok say
                    "-acodec", "libmp3lame",
                    "-ab", self.bitrate,
                    "-map_metadata", "0",  # Preserve metadata
                    "-y",  # Üzerine yaz
                    str(output_file)
                ]
                
                # FFmpeg'i çalıştır - thread-safe erişim
                with self.process_lock:
                    # Re-check for cancellation inside the lock to prevent a race condition.
                    if not self.is_running:
                        break
                    try:
                        startupinfo = None
                        if os.name == 'nt':
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        self.current_process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,  # stdout kullanılmıyor, buffer dolmasını önle
                            stderr=subprocess.PIPE,
                            startupinfo=startupinfo
                        )
                        process = self.current_process
                    except (OSError, ValueError):
                        self.current_process = None
                        raise
                
                # İşlem tamamlanana kadar bekle (byte olarak al)
                stdout_bytes, stderr_bytes = process.communicate()
                
                with self.process_lock:
                    self.current_process = None
                
                # Decode stderr - errors='replace' ile geçersiz karakterler görünür kalır
                stderr = stderr_bytes.decode('utf-8', errors='replace')
                
                # İptal edildi mi kontrol et
                if not self.is_running:
                    # Conversion was cancelled, clean up the partial output file.
                    try:
                        if output_file.exists():
                            output_file.unlink()
                            logger.info(f"Cleaned up partial file: {output_file}")
                    except OSError as e:
                        logger.warning(f"Could not clean up partial file {output_file}: {e}")
                    # İptal edildi, bu dosyayı atla
                    continue
                    
                if process.returncode == 0:
                    # Başarılı - orijinal dosyayı sil (eğer ses dosyasıysa ve replace_originals true ise)
                    is_replaced = False
                    if file_ext in self.AUDIO_EXTENSIONS and self.replace_originals:
                        try:
                            input_file.unlink()
                            is_replaced = True
                        except OSError as e:
                            self.error.emit("delete_error", {"file_name": input_file.name, "error": str(e)})
                    
                    self.file_completed.emit(str(input_file), str(output_file), is_replaced)
                else:
                    # Non-zero return code means FFmpeg error (cancellation already handled above)
                    # Log the technical error for debugging
                    if stderr.strip():
                        logger.error(f"FFmpeg error for {input_file.name}: {stderr}")
                    
                    self.error.emit("conversion_error", {"file_name": input_file.name})
                
                # İlerleme güncelle
                progress = int((index + 1) / total_files * 100)
                self.progress.emit(progress)
                
            except (subprocess.SubprocessError, OSError, ValueError) as e:
                self.error.emit("subprocess_error", {"error": str(e)})
                
        self.status.emit("completed" if self.is_running else "cancelled", "")
        
    def stop(self):
        """Dönüştürmeyi durdur"""
        self.is_running = False
        # Thread-safe FFmpeg process sonlandırma
        with self.process_lock:
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
                    self.error.emit("terminate_error", {"error": str(e)})


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
    
    def detect_ffmpeg(self):
        """FFmpeg'i bul ve yolunu döndür"""
        # Önce static-ffmpeg'i dene
        try:
            static_ffmpeg.add_paths()
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                return ffmpeg_path
        except (ImportError, AttributeError, OSError) as e:
            logger.warning(f"Static FFmpeg setup failed: {e}")
        
        # Sistem FFmpeg'ini kontrol et
        return shutil.which('ffmpeg')
    
    def setup_ffmpeg(self):
        """FFmpeg kurulumunu kontrol et ve yükle"""
        self.ffmpeg_path = self.detect_ffmpeg()
        
        if not self.ffmpeg_path:
            QMessageBox.warning(
                self,
                translation_manager.tr("FFmpeg Not Found"),
                translation_manager.tr("FFmpeg not found. MP3 conversion feature is disabled.\n\n"
                       "Please install FFmpeg or restart the application.")
            )
        
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Widget'lar arası genel boşluk
        layout.setContentsMargins(0, 0, 0, 0)  # Ana layout margin kaldır
        
        # Başlık
        self.title_label = QLabel(translation_manager.tr("Convert Any File to MP3"))
        self.title_label.setObjectName("converterTitle")
        layout.addWidget(self.title_label)
        
        # Açıklama
        self.desc_label = QLabel(translation_manager.tr("Convert your video, audio and other media files to MP3 format. "
                     "You can drag and drop files or select them."))
        self.desc_label.setWordWrap(True)
        self.desc_label.setObjectName("converterDescription")
        layout.addWidget(self.desc_label)
        
        # İçerik alanı için layout - padding eklemek için
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 0, 10, 0)  # Sol ve sağ padding
        
        # Dosya seçme butonu
        self.select_btn = QPushButton(translation_manager.tr(" Select File"))
        self.select_btn.setIcon(icon_manager.get_icon("file", "#FFFFFF"))
        self.select_btn.clicked.connect(self.select_files)
        
        # FFmpeg yoksa dosya seçme butonunu da devre dışı bırak
        if not self.ffmpeg_path:
            self.select_btn.setEnabled(False)
            self.select_btn.setToolTip(translation_manager.tr("FFmpeg not found. File selection disabled."))
        style_manager.apply_button_style(self.select_btn, "primary")
        content_layout.addWidget(self.select_btn)
        
        # Dosya listesi - genişleyebilir alan
        self.file_list = DragDropListWidget()
        # Set object name for theme-specific styling
        self.file_list.setObjectName("converterFileList")
        self.file_list.files_dropped.connect(self.add_files)
        self.file_list.clicked_when_empty.connect(self.select_files)  # Boş listeye tıklandığında dosya seç
        
        content_layout.addWidget(self.file_list)
        
        layout.addLayout(content_layout, 1)  # stretch factor 1 - bu alan genişleyecek
        
        # Alt kısım için sabit layout
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(10)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)
        
        # Durum etiketi
        self.status_label = QLabel("")
        self.status_label.setObjectName("converterStatusLabel")
        bottom_layout.addWidget(self.status_label)
        
        # Ayarlar grubu (başlıksız)
        settings_group = QGroupBox()
        settings_group.setObjectName("converterSettingsGroup")
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(10, 5, 10, 5)  # İçerik kenar boşlukları
        settings_layout.setSpacing(5)  # Widget'lar arası boşluk
        
        # Orijinal dosyaları silme seçeneği
        self.replace_checkbox = QCheckBox(translation_manager.tr("Delete original files after conversion"))
        self.replace_checkbox.setChecked(True)
        self.replace_checkbox.setToolTip(translation_manager.tr("If checked, original files will be deleted after conversion."))
        self.replace_checkbox.stateChanged.connect(self.on_replace_checkbox_changed)
        settings_layout.addWidget(self.replace_checkbox)
        
        # Uyarı mesajı - checkbox'un hemen altında
        self.warning_label = QLabel(translation_manager.tr("WARNING: Original audio files (WAV, FLAC, M4A etc.) will be permanently deleted. Video files are always preserved."))
        self.warning_label.setWordWrap(True)
        self.warning_label.setObjectName("alertWarning")
        self.warning_label.setVisible(self.replace_checkbox.isChecked())  # Başlangıçta checkbox durumuna göre göster/gizle
        settings_layout.addWidget(self.warning_label)
        
        settings_group.setLayout(settings_layout)
        bottom_layout.addWidget(settings_group)
        
        # Butonlar - en altta
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 0, 10, 10)  # Butonlar için yan ve alt margin
        
        self.convert_btn = QPushButton(translation_manager.tr(" Start Conversion"))
        self.convert_btn.setIcon(icon_manager.get_icon("refresh-cw", "#FFFFFF"))
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        
        # FFmpeg yoksa butonu devre dışı bırak
        if not self.ffmpeg_path:
            self.convert_btn.setToolTip(translation_manager.tr("FFmpeg not found. Conversion feature unavailable."))
        style_manager.apply_button_style(self.convert_btn, "secondary")
        button_layout.addWidget(self.convert_btn)
        
        self.cancel_btn = QPushButton(translation_manager.tr(" Cancel"))
        self.cancel_btn.setIcon(icon_manager.get_icon("x", "#FFFFFF"))
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setVisible(False)
        style_manager.apply_button_style(self.cancel_btn, "warning")
        button_layout.addWidget(self.cancel_btn)
        
        self.clear_btn = QPushButton(translation_manager.tr(" Clear List"))
        self.clear_btn.setIcon(icon_manager.get_icon("trash-2", "#FFFFFF"))
        self.clear_btn.clicked.connect(self.clear_list)
        style_manager.apply_button_style(self.clear_btn, "warning")
        button_layout.addWidget(self.clear_btn)
        
        bottom_layout.addLayout(button_layout)
        
        # Alt layout'u ana layout'a ekle
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
    def on_replace_checkbox_changed(self):
        """Checkbox durumu değiştiğinde"""
        # Checkbox işaretli ise uyarıyı göster, değilse gizle
        self.warning_label.setVisible(self.replace_checkbox.isChecked())
        
        # Listedeki ses dosyalarının açıklamalarını güncelle
        for file_path, item in self.file_items.items():
            file_ext = Path(file_path).suffix.lower()
            file_name = html.escape(os.path.basename(file_path))
            
            # Sadece ses dosyalarını güncelle ve henüz dönüştürülmemiş olanları
            if file_ext in ConversionWorker.AUDIO_EXTENSIONS and item.data(Qt.UserRole + 1) != 'completed':
                if self.replace_checkbox.isChecked():
                    item.setText("🎵 {} ({})".format(file_name, translation_manager.tr("Original will be deleted")))
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
            translation_manager.tr("Select Files to Convert"),
            "",
            f"{translation_manager.tr('Supported Files')} ({all_exts});;{translation_manager.tr('Video Files')} ({video_exts});;{translation_manager.tr('Audio Files')} ({audio_exts});;{translation_manager.tr('All Files')} (*.*)"
        )
        
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        """Dosyaları listeye ekle"""
        # FFmpeg yoksa dosya eklemeye izin verme
        if not self.ffmpeg_path:
            QMessageBox.warning(
                self, 
                translation_manager.tr("FFmpeg Required"), 
                translation_manager.tr("FFmpeg is required for conversion feature. Please install FFmpeg or restart the application.")
            )
            return
        
        # Batch UI updates for performance
        self.file_list.setUpdatesEnabled(False)
        
        try:
            mp3_skipped_count = 0
            added_count = 0
            
            for file_path in files:
                # MP3 dosyalarını ekleme
                if file_path.lower().endswith('.mp3'):
                    mp3_skipped_count += 1
                    continue
                    
                # Zaten listede var mı kontrol et
                if file_path not in self.selected_files:
                    self.selected_files.add(file_path)
                    added_count += 1
                    
                    # Dosya tipine göre ikon ve bilgi ekle
                    file_ext = Path(file_path).suffix.lower()
                    file_name = html.escape(os.path.basename(file_path))
                    
                    if file_ext in ConversionWorker.AUDIO_EXTENSIONS:
                        if self.replace_checkbox.isChecked():
                            display_text = "🎵 {} ({})".format(file_name, translation_manager.tr("Original will be deleted"))
                        else:
                            display_text = "🎵 {}".format(file_name)
                    elif file_ext in ConversionWorker.VIDEO_EXTENSIONS:
                        display_text = "🎬 {}".format(file_name)
                    else:
                        display_text = "📄 {}".format(file_name)
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, file_path)
                    item.setData(Qt.UserRole + 1, 'pending')  # Store conversion state
                    self.file_list.addItem(item)
                    self.file_items[file_path] = item  # Store for O(1) lookup
        finally:
            # Re-enable updates
            self.file_list.setUpdatesEnabled(True)
            
        # Update status label once after all files are processed
        if mp3_skipped_count > 0 and added_count == 0:
            self.status_label.setText(translation_manager.tr("{} MP3 files skipped").format(mp3_skipped_count))
            style_manager.apply_alert_style(self.status_label, "warning")
        elif self.selected_files and self.ffmpeg_path:
            self.convert_btn.setEnabled(True)
            if added_count > 0:
                self.status_label.setText(translation_manager.tr("{} files added (total {})").format(added_count, len(self.selected_files)))
            else:
                self.status_label.setText(translation_manager.tr("{} files selected").format(len(self.selected_files)))
            style_manager.apply_alert_style(self.status_label, "success")
        elif self.selected_files and not self.ffmpeg_path:
            self.status_label.setText(translation_manager.tr("FFmpeg not found - Conversion not possible"))
            style_manager.apply_alert_style(self.status_label, "error")
            
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
        
    def update_status(self, status_code, data):
        """Durum güncelle - translate status codes"""
        if status_code == "converting":
            status_text = translation_manager.tr("Converting: {}").format(html.escape(data))
        elif status_code == "completed":
            status_text = translation_manager.tr("Conversion completed!")
        elif status_code == "cancelled":
            status_text = translation_manager.tr("Cancelled")
        else:
            status_text = html.escape(str(data))  # Fallback
            
        self.status_label.setText(status_text)
        style_manager.apply_alert_style(self.status_label, "info")
        
    def file_completed(self, input_path, output_path, is_replaced):  # output_path kept for signal compatibility
        """Dosya tamamlandığında"""
        # O(1) lookup ile hızlı bul
        if input_path in self.file_items:
            item = self.file_items[input_path]
            file_name = html.escape(os.path.basename(input_path))
            file_ext = Path(input_path).suffix.lower()
            
            # Dosya tipine göre orijinal ikonu belirle
            if file_ext in ConversionWorker.AUDIO_EXTENSIONS:
                icon = "🎵"
            elif file_ext in ConversionWorker.VIDEO_EXTENSIONS:
                icon = "🎬"
            else:
                icon = "📄"
            
            # Tamamlanmış metni oluştur
            if is_replaced:
                item.setText("✓ {} {} → MP3 ({})".format(icon, file_name, translation_manager.tr("Original deleted")))
            else:
                item.setText("✓ {} {} → MP3".format(icon, file_name))
            item.setForeground(QColor("green"))
            item.setData(Qt.UserRole + 1, 'completed')  # Update conversion state
                
    def show_error(self, error_code, data_dict):
        """Hata göster - translate error codes"""
        if error_code == "conversion_error":
            error_text = translation_manager.tr("Error ({}): File could not be converted. Please check that the file is not corrupted and is in a supported format.").format(html.escape(data_dict.get("file_name", "Unknown")))
        elif error_code == "delete_error":
            file_name = html.escape(data_dict.get("file_name", "Unknown"))
            error_str = html.escape(data_dict.get("error", "Unknown error"))
            error_text = translation_manager.tr("Original file could not be deleted ({}): {}").format(file_name, error_str)
        elif error_code == "subprocess_error":
            error_text = translation_manager.tr("Conversion error: {}").format(data_dict.get("error", "Unknown error"))
        elif error_code == "terminate_error":
            error_text = translation_manager.tr("Could not terminate FFmpeg process: {}").format(data_dict.get("error", "Unknown error"))
        else:
            error_text = str(data_dict)  # Fallback
            
        QMessageBox.warning(self, translation_manager.tr("Error"), error_text)
        
    def cancel_conversion(self):
        """Dönüştürme işlemini iptal et"""
        if self.conversion_worker:
            self.conversion_worker.stop()
            self.status_label.setText(translation_manager.tr("Cancelling..."))
            style_manager.apply_alert_style(self.status_label, "warning")
    
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
                translation_manager.tr("Completed"),
                translation_manager.tr("All files successfully converted to MP3!")
            )
            
        self.conversion_worker = None
    
    def retranslateUi(self):
        """UI metinlerini yeniden çevir"""
        # Başlık ve açıklama
        if hasattr(self, 'title_label'):
            self.title_label.setText(translation_manager.tr("Convert Any File to MP3"))
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(translation_manager.tr("Convert your video, audio and other media files to MP3 format. "
                                   "You can drag and drop files or select them."))
        
        # Butonlar
        if hasattr(self, 'select_btn'):
            self.select_btn.setText(translation_manager.tr(" Select File"))
        if hasattr(self, 'convert_btn'):
            self.convert_btn.setText(translation_manager.tr(" Start Conversion"))
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setText(translation_manager.tr(" Cancel"))
        if hasattr(self, 'clear_btn'):
            self.clear_btn.setText(translation_manager.tr(" Clear List"))
        
        # Checkbox ve uyarı
        if hasattr(self, 'replace_checkbox'):
            self.replace_checkbox.setText(translation_manager.tr("Delete original files after conversion"))
            self.replace_checkbox.setToolTip(translation_manager.tr("If checked, original files will be deleted after conversion."))
        if hasattr(self, 'warning_label'):
            self.warning_label.setText(translation_manager.tr("WARNING: Original audio files (WAV, FLAC, M4A etc.) will be permanently deleted. Video files are always preserved."))
        
        # Mevcut dosya listesindeki öğeleri güncelle
        if hasattr(self, 'file_list') and hasattr(self, 'file_items'):
            for file_path, item in self.file_items.items():
                # Dönüştürme durumunu kontrol et
                conversion_state = item.data(Qt.UserRole + 1)
                file_ext = Path(file_path).suffix.lower()
                file_name = html.escape(os.path.basename(file_path))
                
                # Dosya tipine göre ikon belirle
                if file_ext in ConversionWorker.AUDIO_EXTENSIONS:
                    icon = "🎵"
                elif file_ext in ConversionWorker.VIDEO_EXTENSIONS:
                    icon = "🎬"
                else:
                    icon = "📄"
                
                # Duruma göre metni güncelle
                if conversion_state == 'completed':
                    # Get the original replaced state from the item text
                    if translation_manager.tr("Original deleted") in item.text():
                        item.setText("✓ {} {} → MP3 ({})".format(icon, file_name, translation_manager.tr("Original deleted")))
                    else:
                        item.setText("✓ {} {} → MP3".format(icon, file_name))
                elif conversion_state == 'pending':
                    # Henüz dönüştürülmemiş dosyalar
                    if file_ext in ConversionWorker.AUDIO_EXTENSIONS and self.replace_checkbox.isChecked():
                        item.setText("{} {} ({})".format(icon, file_name, translation_manager.tr("Original will be deleted")))
                    else:
                        item.setText("{} {}".format(icon, file_name))
        
        # Liste widget'ı güncelle
        self.file_list.viewport().update()
