from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                            QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from database.manager import DatabaseManager
from datetime import datetime


class HistoryWidget(QWidget):
    """İndirme geçmişi widget'ı"""
    
    # Dosyayı tekrar indir sinyali
    redownload_signal = pyqtSignal(str)  # URL
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
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
        
        self.refresh_button = QPushButton("🔄 Yenile")
        self.refresh_button.clicked.connect(self.load_history)
        search_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton("🗑️ Geçmişi Temizle")
        self.clear_button.clicked.connect(self.clear_history)
        search_layout.addWidget(self.clear_button)
        
        layout.addLayout(search_layout)
        
        # İstatistikler
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Başlık", "Kanal", "Format", "Boyut", "İşlemler"
        ])
        
        # Tablo ayarları
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Başlık sütunu genişlesin
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def load_history(self):
        """Geçmişi yükle"""
        history = self.db_manager.get_all_downloads()
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
            
            # Tekrar indir butonu
            redownload_btn = QPushButton("🔄")
            redownload_btn.setToolTip("Tekrar İndir")
            redownload_btn.setMaximumWidth(30)
            redownload_btn.clicked.connect(lambda checked, url=record['url']: self.redownload(url))
            actions_layout.addWidget(redownload_btn)
            
            # Sil butonu
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Geçmişten Sil")
            delete_btn.setMaximumWidth(30)
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
            f"📊 Toplam: {stats['total_downloads']} dosya | "
            f"💾 {stats['total_size_mb']:.1f} MB | "
            f"📅 Bugün: {stats['today_downloads']} dosya"
        )
        
        self.stats_label.setText(stats_text)
    
    def redownload(self, url):
        """URL'yi tekrar indir"""
        self.redownload_signal.emit(url)
    
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