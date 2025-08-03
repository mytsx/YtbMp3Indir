from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                            QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QThread
from PyQt5.QtGui import QDesktopServices
from database.manager import DatabaseManager
from datetime import datetime
from styles import style_manager


class HistoryWidget(QWidget):
    """İndirme geçmişi widget'ı"""
    
    # Dosyayı tekrar indir sinyali
    redownload_signal = pyqtSignal(str)  # URL
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        
        # Buton stilleri artık style_manager tarafından yönetiliyor
        
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout()
        
        # Arama ve filtre alanı
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Şarkı adı veya kanal ara...")
        self.search_input.textChanged.connect(self.search_history)
        search_layout.addWidget(self.search_input)
        
        self.refresh_button = QPushButton("↻ Yenile")
        self.refresh_button.clicked.connect(self.load_history)
        style_manager.apply_button_style(self.refresh_button, "secondary")
        search_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton("🗑 Geçmişi Temizle")
        self.clear_button.clicked.connect(self.clear_history)
        style_manager.apply_button_style(self.clear_button, "danger")
        search_layout.addWidget(self.clear_button)
        
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Başlık", "Kanal", "Format", "Boyut", "İşlemler"
        ])
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)  # Son sütun gereksiz genişlemesin
        
        # Sütun genişliklerini manuel olarak ayarla
        self.table.setColumnWidth(0, 130)  # Tarih - sabit genişlik
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Başlık - geri kalan alanı kaplasın
        self.table.setColumnWidth(2, 120)  # Kanal - daha dar
        self.table.setColumnWidth(3, 80)   # Format - içerik görünsün
        self.table.setColumnWidth(4, 90)   # Boyut - içerik görünsün
        self.table.setColumnWidth(5, 140)  # İşlemler - scrollbar'dan uzak durması için daha geniş
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Düzenleme kapalı
        
        # Satır yüksekliğini ayarla - butonların görünmesi için
        self.table.verticalHeader().setDefaultSectionSize(42)  # 42px yükseklik
        self.table.verticalHeader().setMinimumSectionSize(40)  # Minimum 40px
        
        # Satır numarası sütununu daralt
        self.table.verticalHeader().setMaximumWidth(25)  # Maksimum 25px genişlik
        self.table.verticalHeader().setMinimumWidth(20)  # Minimum 20px
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)  # Sayıları ortala
        
        layout.addWidget(self.table)
        
        # İstatistikler - tablonun altında
        self.stats_label = QLabel()
        self.stats_label.setObjectName("statsLabel")
        layout.addWidget(self.stats_label)
        self.setLayout(layout)
    
    def load_history(self):
        """Geçmişi yükle"""
        # Loading göstergesi
        self.table.setRowCount(0)
        loading_row = self.table.rowCount()
        self.table.insertRow(loading_row)
        loading_item = QTableWidgetItem("Yükleniyor...")
        loading_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(loading_row, 1, loading_item)
        self.table.setSpan(loading_row, 1, 1, 5)  # Tüm sütunları kapla
        
        # Thread'de yükle
        class LoadThread(QThread):
            data_loaded = pyqtSignal(list)
            
            def __init__(self, db_manager):
                super().__init__()
                self.db_manager = db_manager
                
            def run(self):
                history = self.db_manager.get_all_downloads()
                self.data_loaded.emit(history)
        
        # Eski thread varsa bekle
        if hasattr(self, 'load_thread') and self.load_thread.isRunning():
            self.load_thread.wait()
            
        self.load_thread = LoadThread(self.db_manager)
        self.load_thread.data_loaded.connect(self.on_history_loaded)
        self.load_thread.start()
    
    def on_history_loaded(self, history):
        """Geçmiş yüklendiğinde"""
        self.display_history(history)
        self.update_statistics()
    
    def display_history(self, history):
        """Geçmişi tabloda göster"""
        self.table.setRowCount(0)
        
        for record in history:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Tarih
            date_str = datetime.fromisoformat(record['downloaded_at']).strftime('%d.%m.%Y %H:%M')
            self.table.setItem(row_position, 0, QTableWidgetItem(date_str))
            
            # Başlık
            self.table.setItem(row_position, 1, QTableWidgetItem(record['video_title']))
            
            # Kanal
            self.table.setItem(row_position, 2, QTableWidgetItem(record['channel_name'] or '-'))
            
            # Format
            self.table.setItem(row_position, 3, QTableWidgetItem(record['format'].upper()))
            
            # Boyut
            size_mb = record['file_size'] / (1024 * 1024) if record['file_size'] else 0
            size_str = f"{size_mb:.1f} MB" if size_mb > 0 else "-"
            self.table.setItem(row_position, 4, QTableWidgetItem(size_str))
            
            # İşlemler butonu
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(1)
            
            # Tarayıcıda aç butonu
            browser_btn = QPushButton()
            browser_btn.setText("🌐")  # Globe emoji
            browser_btn.setToolTip("Tarayıcıda Aç")
            browser_btn.setFixedSize(24, 24)
            style_manager.apply_button_style(browser_btn, "icon")
            browser_btn.setStyleSheet(browser_btn.styleSheet() + "\nQPushButton { background-color: #2196F3; }")
            browser_btn.clicked.connect(lambda checked, url=record['url']: self.open_in_browser(url))
            actions_layout.addWidget(browser_btn)
            
            # Tekrar indir butonu
            redownload_btn = QPushButton()
            redownload_btn.setText("↻")  # Reload symbol
            redownload_btn.setToolTip("Tekrar İndir")
            redownload_btn.setFixedSize(24, 24)
            style_manager.apply_button_style(redownload_btn, "icon")
            redownload_btn.setStyleSheet(redownload_btn.styleSheet() + "\nQPushButton { background-color: #4CAF50; }")
            redownload_btn.clicked.connect(lambda checked, url=record['url']: self.redownload(url))
            actions_layout.addWidget(redownload_btn)
            
            # Sil butonu
            delete_btn = QPushButton()
            delete_btn.setText("×")  # Simple X character
            delete_btn.setToolTip("Geçmişten Sil")
            delete_btn.setFixedSize(24, 24)
            style_manager.apply_button_style(delete_btn, "icon")
            delete_btn.setStyleSheet(delete_btn.styleSheet() + "\nQPushButton { background-color: #f44336; }")
            delete_btn.clicked.connect(lambda checked, id=record['id']: self.delete_record(id))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row_position, 5, actions_widget)
    
    def search_history(self, text):
        """Geçmişte arama yap"""
        if text.strip():
            history = self.db_manager.search_downloads(text)
        else:
            history = self.db_manager.get_all_downloads()
        self.display_history(history)
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        stats = self.db_manager.get_statistics()
        
        stats_text = (
            f"Toplam: {stats['total_downloads']} dosya | "
            f"Boyut: {stats['total_size_mb']:.1f} MB | "
            f"Bugün: {stats['today_downloads']} dosya"
        )
        
        self.stats_label.setText(stats_text)
    
    def redownload(self, url):
        """URL'yi tekrar indir"""
        self.redownload_signal.emit(url)
    
    def open_in_browser(self, url):
        """URL'yi tarayıcıda aç"""
        QDesktopServices.openUrl(QUrl(url))
    
    def delete_record(self, record_id):
        """Kaydı sil"""
        reply = QMessageBox.question(
            self, 
            "Onay", 
            "Bu kaydı geçmişten silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_download(record_id):
                self.load_history()
    
    def clear_history(self):
        """Tüm geçmişi temizle"""
        reply = QMessageBox.question(
            self, 
            "Onay", 
            "Tüm indirme geçmişini silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            count = self.db_manager.clear_history()
            QMessageBox.information(self, "Başarılı", f"{count} kayıt silindi.")
            self.load_history()
    
    def mousePressEvent(self, a0):
        """Mouse tıklaması olduğunda"""
        # Tıklanan widget'ı kontrol et
        widget = self.childAt(a0.pos())
        
        # Eğer tablo dışında bir yere tıklandıysa seçimi temizle
        if widget != self.table and not self.table.isAncestorOf(widget):
            self.table.clearSelection()
        
        # Normal event işlemeye devam et
        super().mousePressEvent(a0)