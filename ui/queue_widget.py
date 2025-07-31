from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                           QMenu, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QMouseEvent
from database.manager import DatabaseManager
from datetime import datetime


class QueueWidget(QWidget):
    """İndirme kuyruğu yönetim widget'ı"""
    
    # Sinyaller
    start_download = pyqtSignal(dict)  # Kuyruktan indirme başlat
    queue_updated = pyqtSignal()  # Kuyruk güncellendiğinde
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.init_ui()
        self.load_queue()
        
        # Otomatik yenileme
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_queue)
        self.refresh_timer.start(5000)  # 5 saniyede bir yenile
        
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout()
        
        # Buton stilleri (bir kere tanımla)
        self.button_style_up_down = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 1px solid #1976D2;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border-color: #0D47A1;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """
        
        self.button_style_delete = """
            QPushButton {
                background-color: #f44336;
                color: white;
                border: 1px solid #d32f2f;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """
        
        # Üst kontrol paneli
        control_layout = QHBoxLayout()
        
        # Başlık
        title_label = QLabel("İndirme Kuyruğu")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Durum filtresi
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tümü", "Bekliyor", "İndiriliyor", "Tamamlandı", "Başarısız"])
        self.status_filter.currentTextChanged.connect(self.filter_by_status)
        
        # Kontrol butonları
        self.start_button = QPushButton("▶ Kuyruğu Başlat")
        self.start_button.clicked.connect(self.start_queue)
        
        self.pause_button = QPushButton("⏸ Duraklat")
        self.pause_button.clicked.connect(self.pause_queue)
        self.pause_button.setEnabled(False)
        
        self.clear_completed_button = QPushButton("✓ Tamamlananları Temizle")
        self.clear_completed_button.clicked.connect(self.clear_completed)
        
        control_layout.addWidget(title_label)
        control_layout.addStretch()
        control_layout.addWidget(QLabel("Filtre:"))
        control_layout.addWidget(self.status_filter)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.clear_completed_button)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "URL/Başlık", "Durum", 
            "Eklenme Zamanı", "İşlem"
        ])
        
        # Tablo ayarları
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Düzenleme kapalı
        self.table.horizontalHeader().setStretchLastSection(False)
        # URL/Başlık sütunu genişlesin, diğerleri içerik kadar olsun
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # URL/Başlık
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Durum
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Eklenme Zamanı
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # İşlem
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # İstatistikler
        self.stats_label = QLabel("Toplam: 0 | Bekleyen: 0 | Tamamlanan: 0")
        
        # Layout'a ekle
        layout.addLayout(control_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
        
    def load_queue(self):
        """Kuyruğu veritabanından yükle"""
        # Filtre durumunu al
        filter_status = None
        if self.status_filter.currentText() != "Tümü":
            status_map = {
                "Bekliyor": "pending",
                "İndiriliyor": "downloading",
                "Tamamlandı": "completed",
                "Başarısız": "failed"
            }
            filter_status = status_map.get(self.status_filter.currentText())
        
        # Veritabanından öğeleri al
        items = self.db.get_queue_items(filter_status)
        
        # Tabloyu güncelle
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # URL/Başlık
            title = item['video_title'] or item['url']
            title_item = QTableWidgetItem(title)
            title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)  # Düzenleme kapalı
            self.table.setItem(row, 0, title_item)
            
            # Durum
            status_text = self.get_status_text(item['status'])
            status_item = QTableWidgetItem(status_text)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)  # Düzenleme kapalı
            self.set_status_style(status_item, item['status'])
            self.table.setItem(row, 1, status_item)
            
            # Eklenme zamanı
            added_time = datetime.fromisoformat(item['added_at']).strftime("%d.%m.%Y %H:%M")
            time_item = QTableWidgetItem(added_time)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)  # Düzenleme kapalı
            self.table.setItem(row, 2, time_item)
            
            # İşlem butonları - geçmiş tabındaki gibi kompakt
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(2)
            
            # Yukarı taşı
            up_button = QPushButton("↑")
            up_button.setFixedSize(28, 28)
            up_button.setToolTip("Yukarı Taşı")
            up_button.setStyleSheet(self.button_style_up_down)
            up_button.clicked.connect(lambda checked, id=item['id']: self.move_up(id))
            
            # Aşağı taşı
            down_button = QPushButton("↓")
            down_button.setFixedSize(28, 28)
            down_button.setToolTip("Aşağı Taşı")
            down_button.setStyleSheet(self.button_style_up_down)
            down_button.clicked.connect(lambda checked, id=item['id']: self.move_down(id))
            
            # Sil
            delete_button = QPushButton("×")
            delete_button.setFixedSize(28, 28)
            delete_button.setToolTip("Kuyruktan Kaldır")
            delete_button.setStyleSheet(self.button_style_delete)
            delete_button.clicked.connect(lambda checked, id=item['id']: self.delete_item(id))
            
            action_layout.addWidget(up_button)
            action_layout.addWidget(down_button)
            action_layout.addWidget(delete_button)
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(row, 3, action_widget)
            
            # ID'yi ilk sütundaki item'a userData olarak sakla
            self.table.item(row, 0).setData(Qt.UserRole, item['id'])
        
        # İstatistikleri güncelle
        self.update_statistics()
        
    def get_status_text(self, status):
        """Durum metnini döndür"""
        status_map = {
            'pending': 'Bekliyor',
            'downloading': 'İndiriliyor',
            'converting': 'Dönüştürülüyor',
            'completed': 'Tamamlandı',
            'failed': 'Başarısız',
            'paused': 'Duraklatıldı'
        }
        return status_map.get(status, status)
    
    def set_status_style(self, item, status):
        """Durum stilini ayarla"""
        if status == 'pending':
            item.setForeground(Qt.darkGray)
        elif status == 'downloading':
            item.setForeground(Qt.blue)
        elif status == 'converting':
            item.setForeground(Qt.darkMagenta)
        elif status == 'completed':
            item.setForeground(Qt.darkGreen)
        elif status == 'failed':
            item.setForeground(Qt.red)
        elif status == 'paused':
            item.setForeground(Qt.darkYellow)
    
    def get_priority_text(self, priority):
        """Öncelik metnini döndür"""
        if priority >= 2:
            return "Yüksek"
        elif priority == 1:
            return "Normal"
        else:
            return "Düşük"
    
    def filter_by_status(self, status_text):
        """Duruma göre filtrele"""
        self.load_queue()
    
    def start_queue(self):
        """Kuyruğu başlat"""
        # İndiriliyor durumunda kalmış olanları düzelt
        self.db.reset_stuck_downloads()
        
        # Sıradaki öğeyi al
        next_item = self.db.get_next_queue_item()
        if next_item:
            self.start_download.emit(next_item)
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
        else:
            QMessageBox.information(self, "Bilgi", "Kuyrukta bekleyen indirme yok.")
    
    def pause_queue(self):
        """Kuyruğu duraklat"""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
    
    def clear_completed(self):
        """Tamamlananları temizle"""
        count = self.db.clear_queue('completed')
        # Kalan öğelerin pozisyonlarını yeniden düzenle
        self.db.reorder_queue_positions()
        self.load_queue()
        QMessageBox.information(self, "Bilgi", f"{count} tamamlanmış indirme kaldırıldı.")
    
    def move_up(self, item_id):
        """Öğeyi yukarı taşı"""
        # Mevcut pozisyonu bul
        items = self.db.get_queue_items()
        current_item = next((item for item in items if item['id'] == item_id), None)
        
        if current_item and current_item['position'] > 1:
            # Üstteki öğeyi bul
            above_item = next((item for item in items 
                             if item['position'] == current_item['position'] - 1), None)
            
            if above_item:
                # Pozisyonları değiştir
                self.db.update_queue_position(item_id, current_item['position'] - 1)
                self.db.update_queue_position(above_item['id'], current_item['position'])
                self.load_queue()
    
    def move_down(self, item_id):
        """Öğeyi aşağı taşı"""
        # Mevcut pozisyonu bul
        items = self.db.get_queue_items()
        current_item = next((item for item in items if item['id'] == item_id), None)
        max_position = max(item['position'] for item in items) if items else 0
        
        if current_item and current_item['position'] < max_position:
            # Alttaki öğeyi bul
            below_item = next((item for item in items 
                             if item['position'] == current_item['position'] + 1), None)
            
            if below_item:
                # Pozisyonları değiştir
                self.db.update_queue_position(item_id, current_item['position'] + 1)
                self.db.update_queue_position(below_item['id'], current_item['position'])
                self.load_queue()
    
    def delete_item(self, item_id):
        """Öğeyi sil"""
        reply = QMessageBox.question(self, "Onay", 
                                   "Bu öğeyi kuyruktan kaldırmak istiyor musunuz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.db.remove_from_queue(item_id)
            self.load_queue()
            self.queue_updated.emit()
    
    def show_context_menu(self, position):
        """Sağ tık menüsü göster"""
        if self.table.currentRow() < 0:
            return
        
        menu = QMenu()
        
        # Seçili öğenin ID'sini userData'dan al
        item_id = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
        
        # Menü öğeleri
        retry_action = menu.addAction("Tekrar Dene")
        retry_action.triggered.connect(lambda: self.retry_item(item_id))
        
        priority_menu = menu.addMenu("Öncelik")
        high_priority = priority_menu.addAction("Yüksek")
        high_priority.triggered.connect(lambda: self.set_priority(item_id, 2))
        
        normal_priority = priority_menu.addAction("Normal")
        normal_priority.triggered.connect(lambda: self.set_priority(item_id, 1))
        
        low_priority = priority_menu.addAction("Düşük")
        low_priority.triggered.connect(lambda: self.set_priority(item_id, 0))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Sil")
        delete_action.triggered.connect(lambda: self.delete_item(item_id))
        
        menu.exec_(self.table.mapToGlobal(position))
    
    def retry_item(self, item_id):
        """Başarısız öğeyi tekrar dene"""
        self.db.update_queue_status(item_id, 'pending')
        self.load_queue()
    
    def set_priority(self, item_id, priority):
        """Öncelik ayarla"""
        # Veritabanı bağlantısını doğrudan kullan
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE download_queue SET priority = ? WHERE id = ?', 
                         (priority, item_id))
            conn.commit()
        self.load_queue()
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        items = self.db.get_queue_items()
        total = len(items)
        pending = sum(1 for item in items if item['status'] == 'pending')
        completed = sum(1 for item in items if item['status'] == 'completed')
        
        self.stats_label.setText(f"Toplam: {total} | Bekleyen: {pending} | Tamamlanan: {completed}")
    
    def add_to_queue(self, url, title=None):
        """Kuyruğa yeni öğe ekle"""
        self.db.add_to_queue(url, title)
        self.load_queue()
        self.queue_updated.emit()
    
    def update_download_status(self, queue_id, status, error_message=None):
        """İndirme durumunu güncelle"""
        self.db.update_queue_status(queue_id, status, error_message)
        self.load_queue()
        
        # Tamamlandıysa veya başarısızsa, sıradakini başlat
        if status in ['completed', 'failed'] and self.pause_button.isEnabled():
            QTimer.singleShot(1000, self.start_queue)
    
    def mousePressEvent(self, a0: QMouseEvent):
        """Mouse tıklaması olduğunda"""
        # Tıklanan widget'ı kontrol et
        widget = self.childAt(a0.pos())
        
        # Eğer tablo dışında bir yere tıklandıysa seçimi temizle
        if widget != self.table and not self.table.isAncestorOf(widget):
            self.table.clearSelection()
        
        # Normal event işlemeye devam et
        super().mousePressEvent(a0)