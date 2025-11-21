from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                           QMenu, QMessageBox, QComboBox, QLineEdit, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QMouseEvent, QKeySequence
from database.manager import DatabaseManager
from datetime import datetime
from styles import style_manager
from utils.icon_manager import icon_manager
from utils.translation_manager import translation_manager


class QueueWidget(QWidget):
    """İndirme kuyruğu yönetim widget'ı"""
    
    # Sinyaller
    start_download = pyqtSignal(dict)  # Kuyruktan indirme başlat
    queue_updated = pyqtSignal()  # Kuyruk güncellendiğinde
    queue_started = pyqtSignal()  # Normal kuyruk başlatıldığında
    queue_paused = pyqtSignal()  # Kuyruk duraklatıldığında
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.current_items_hash = None  # Mevcut liste hash'i
        self.init_ui()
        self.setup_keyboard_shortcuts()
        self.load_queue()
        
        # Otomatik yenileme
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_and_refresh)
        self.refresh_timer.start(5000)  # 5 saniyede bir kontrol et
        
    def init_ui(self):
        """Arayüzü oluştur"""
        layout = QVBoxLayout()
        
        
        # Üst kontrol paneli
        control_layout = QHBoxLayout()
        
        # Başlık
        self.title_label = QLabel(translation_manager.tr("queue.title"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        control_layout.addWidget(self.title_label)
        control_layout.addStretch()
        
        # Kontrol butonları
        self.start_button = QPushButton(translation_manager.tr("queue.buttons.start_queue"))
        self.start_button.setIcon(icon_manager.get_icon("play", "#FFFFFF"))
        self.start_button.clicked.connect(self.start_queue)
        self.start_button.setToolTip(translation_manager.tr("queue.tooltips.start_queue"))
        style_manager.apply_button_style(self.start_button, "primary")
        
        self.pause_button = QPushButton(translation_manager.tr("queue.buttons.pause_all"))
        self.pause_button.setIcon(icon_manager.get_icon("pause", "#FFFFFF"))
        self.pause_button.clicked.connect(self.pause_queue)
        self.pause_button.setEnabled(False)
        self.pause_button.setToolTip(translation_manager.tr("queue.tooltips.pause_queue"))
        style_manager.apply_button_style(self.pause_button, "warning")
        
        # Temizleme butonları için dropdown menü
        self.clear_button = QPushButton(translation_manager.tr("queue.buttons.clear"))
        self.clear_button.setIcon(icon_manager.get_icon("trash-2", "#FFFFFF"))
        self.clear_button.setToolTip(translation_manager.tr("queue.tooltips.clear_options"))
        style_manager.apply_button_style(self.clear_button, "danger")
        
        # Temizleme menüsü
        self.clear_menu = QMenu(self)
        
        self.clear_all_action = self.clear_menu.addAction(translation_manager.tr("queue.menu.clear_all"))
        self.clear_all_action.setIcon(icon_manager.get_icon("trash-2", "#DC3545"))
        self.clear_all_action.triggered.connect(self.clear_all)
        
        self.clear_selected_action = self.clear_menu.addAction(translation_manager.tr("queue.menu.clear_selected"))
        self.clear_selected_action.setIcon(icon_manager.get_icon("check-square", "#DC3545"))
        self.clear_selected_action.triggered.connect(self.clear_selected)
        
        self.clear_completed_action = self.clear_menu.addAction(translation_manager.tr("queue.menu.clear_completed"))
        self.clear_completed_action.setIcon(icon_manager.get_icon("check-circle", "#28A745"))
        self.clear_completed_action.triggered.connect(self.clear_completed)
        
        self.clear_failed_action = self.clear_menu.addAction(translation_manager.tr("queue.menu.clear_failed"))
        self.clear_failed_action.setIcon(icon_manager.get_icon("x-circle", "#DC3545"))
        self.clear_failed_action.triggered.connect(self.clear_failed)
        
        self.clear_canceled_action = self.clear_menu.addAction(translation_manager.tr("queue.menu.clear_canceled"))
        self.clear_canceled_action.setIcon(icon_manager.get_icon("slash", "#FFC107"))
        self.clear_canceled_action.triggered.connect(self.clear_canceled)
        
        self.clear_button.setMenu(self.clear_menu)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.clear_button)
        
        # Arama ve filtre alanı - ayrı satırda
        search_layout = QHBoxLayout()
        
        self.search_label = QLabel(translation_manager.tr("queue.labels.search"))
        search_layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translation_manager.tr("queue.placeholders.search"))
        self.search_input.textChanged.connect(self.search_queue)
        search_layout.addWidget(self.search_input)
        
        self.filter_label = QLabel(translation_manager.tr("queue.labels.filter"))
        search_layout.addWidget(self.filter_label)
        self.status_filter = QComboBox()
        # Add items with data (status values)
        self.status_filter.addItem(translation_manager.tr("queue.filters.all"), None)
        self.status_filter.addItem(translation_manager.tr("queue.status.waiting"), "pending")
        self.status_filter.addItem(translation_manager.tr("queue.status.downloading"), "downloading")
        self.status_filter.addItem(translation_manager.tr("queue.status.completed"), "completed")
        self.status_filter.addItem(translation_manager.tr("queue.status.failed"), "failed")
        self.status_filter.currentIndexChanged.connect(self.filter_by_status)
        search_layout.addWidget(self.status_filter)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            translation_manager.tr("queue.columns.title"), translation_manager.tr("queue.columns.status"), 
            translation_manager.tr("queue.columns.added"), translation_manager.tr("queue.columns.action")
        ])
        
        # Tablo ayarları
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)  # Çoklu seçim aktif
        
        # Satır yüksekliğini ayarla - butonların görünmesi için
        self.table.verticalHeader().setDefaultSectionSize(42)  # 42px yükseklik
        self.table.verticalHeader().setMinimumSectionSize(40)  # Minimum 40px
        
        # Satır numarası sütununu daralt ve ortala
        self.table.verticalHeader().setMaximumWidth(25)  # Maksimum 25px genişlik
        self.table.verticalHeader().setMinimumWidth(20)  # Minimum 20px
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)  # Sayıları ortala
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Düzenleme kapalı
        self.table.horizontalHeader().setStretchLastSection(False)
        # Sütun genişliklerini manuel olarak ayarla
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # URL/Başlık - geri kalan alanı kaplasın
        self.table.setColumnWidth(1, 100)  # Durum - sabit genişlik
        self.table.setColumnWidth(2, 130)  # Eklenme Zamanı - sabit genişlik
        self.table.setColumnWidth(3, 140)  # İşlem - butonlar için uygun genişlik
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Durum
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Eklenme Zamanı
        # İşlem sütunu için ResizeToContents KALDIRILDI - sabit genişlik kullanılacak
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # İstatistikler
        self.update_statistics()
        
        # Layout'a ekle
        layout.addLayout(control_layout)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
        
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        # Delete tuşu: Seçili öğeleri sil
        delete_shortcut = QShortcut(QKeySequence.Delete, self)
        delete_shortcut.activated.connect(self.delete_selected_items)
        
        # Space tuşu: Seçili öğeleri duraklat/devam ettir
        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self.toggle_selected_items)
        
        # Ctrl+A: Tümünü seç
        select_all = QShortcut(QKeySequence.SelectAll, self)
        select_all.activated.connect(self.table.selectAll)
        
    def delete_selected_items(self):
        """Seçili öğeleri sil"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
            
        # Seçili satırlardaki öğelerin ID'lerini topla
        queue_ids = []
        for row in selected_rows:
            item_data = self.table.item(row, 0).data(Qt.UserRole)
            if item_data:
                queue_ids.append(item_data['id'])
        
        if queue_ids:
            # Toplu silme işlemi
            deleted_count = self.db.remove_from_queue_batch(queue_ids)
            self.load_queue()
            QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"), translation_manager.tr("queue.messages.items_removed").format(deleted_count))
    
    def toggle_selected_items(self):
        """Seçili öğelerin durumunu değiştir (bekleyen/duraklatıldı)"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
            
        # Seçili öğelerin durumlarını kontrol et ve değiştir
        toggled_count = 0
        for row in selected_rows:
            item_data = self.table.item(row, 0).data(Qt.UserRole)
            if item_data and item_data['status'] == 'pending':
                # Bekleyen öğeleri duraklatılmış yap
                self.db.update_queue_status(item_data['id'], 'paused')
                toggled_count += 1
            elif item_data and item_data['status'] == 'paused':
                # Duraklatılmış öğeleri bekleyen yap
                self.db.update_queue_status(item_data['id'], 'pending')
                toggled_count += 1
        
        if toggled_count > 0:
            self.load_queue()
        
    def check_and_refresh(self):
        """Değişiklik varsa kuyruğu yenile"""
        # Filtre durumunu al - data kullan
        filter_status = self.status_filter.currentData()
        
        # Veritabanından öğeleri al
        items = self.db.get_queue_items(filter_status)
        
        # Liste hash'ini hesapla
        items_hash = hash(str([(item['id'], item['status']) for item in items]))
        
        # Değişiklik varsa güncelle
        if items_hash != self.current_items_hash:
            self.current_items_hash = items_hash
            self.load_queue()
    
    def load_queue(self, force_refresh=False):
        """Kuyruğu veritabanından yükle"""
        # Filtre durumunu al - data kullan
        filter_status = self.status_filter.currentData()
        
        # Veritabanından öğeleri al
        items = self.db.get_queue_items(filter_status)
        
        # Arama filtresi uygula
        search_text = self.search_input.text().strip().lower()
        if search_text:
            items = [item for item in items 
                    if search_text in (item['video_title'] or item['url']).lower()]
        
        # Hash'i güncelle
        if not force_refresh:
            self.current_items_hash = hash(str([(item['id'], item['status']) for item in items]))
        
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
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(2)  # Butonlar arası boşluk arttırıldı
            
            # Hemen indir butonu - pending, failed ve queued durumları için
            if item['status'] in ['pending', 'failed', 'queued']:
                download_button = QPushButton()
                download_button.setIcon(icon_manager.get_icon("download", "#FFFFFF"))
                download_button.setFixedSize(24, 24)
                download_button.setToolTip(translation_manager.tr("queue.menu.download_now"))
                download_button.setObjectName("queueDownloadButton")
                download_button.clicked.connect(lambda checked, id=item['id']: self.download_now(id))
                action_layout.addWidget(download_button)
                action_layout.addSpacing(4)  # İndir butonu ile diğerleri arasına ekstra boşluk
            
            # Yukarı taşı
            up_button = QPushButton()
            up_button.setIcon(icon_manager.get_icon("arrow-up", "#FFFFFF"))
            up_button.setFixedSize(24, 24)
            up_button.setToolTip(translation_manager.tr("queue.buttons.move_up"))
            up_button.setObjectName("upButton")
            up_button.clicked.connect(lambda checked, id=item['id']: self.move_up(id))
            
            # Aşağı taşı
            down_button = QPushButton()
            down_button.setIcon(icon_manager.get_icon("arrow-down", "#FFFFFF"))
            down_button.setFixedSize(24, 24)
            down_button.setToolTip(translation_manager.tr("queue.buttons.move_down"))
            down_button.setObjectName("downButton")
            down_button.clicked.connect(lambda checked, id=item['id']: self.move_down(id))
            
            # Sil
            delete_button = QPushButton()
            delete_button.setIcon(icon_manager.get_icon("x", "#FFFFFF"))
            delete_button.setFixedSize(24, 24)
            delete_button.setToolTip(translation_manager.tr("queue.buttons.remove"))
            delete_button.setObjectName("deleteButton")
            delete_button.clicked.connect(lambda checked, id=item['id']: self.delete_item(id))
            
            action_layout.addWidget(up_button)
            action_layout.addWidget(down_button)
            action_layout.addWidget(delete_button)
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(row, 3, action_widget)
            
            # Tüm item'ı ilk sütundaki item'a userData olarak sakla
            self.table.item(row, 0).setData(Qt.UserRole, item)
        
        # İstatistikleri güncelle
        self.update_statistics()
        
    def get_status_text(self, status):
        """Durum metnini döndür"""
        status_map = {
            'pending': translation_manager.tr("queue.status.waiting"),
            'queued': translation_manager.tr('queue.status.queued'),
            'downloading': translation_manager.tr("queue.status.downloading"),
            'converting': translation_manager.tr('queue.status.converting'),
            'completed': translation_manager.tr("queue.status.completed"),
            'failed': translation_manager.tr("queue.status.failed"),
            'paused': translation_manager.tr('queue.status.paused')
        }
        return status_map.get(status, status)
    
    def set_status_style(self, item, status):
        """Durum stilini ayarla"""
        if status == 'pending':
            item.setForeground(Qt.darkGray)
        elif status == 'queued':
            item.setForeground(Qt.darkCyan)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
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
            return translation_manager.tr("queue.priority.high")
        elif priority == 1:
            return translation_manager.tr("queue.priority.normal")
        else:
            return translation_manager.tr("queue.priority.low")
    
    def filter_by_status(self):
        """Duruma göre filtrele"""
        self.load_queue()
    
    def start_queue(self):
        """Kuyruğu başlat"""
        # İndiriliyor durumunda kalmış olanları düzelt
        self.db.reset_stuck_downloads()
        
        # Kuyruk modunu işaretle
        self.queue_started.emit()
        
        # Sıradaki öğeyi al
        next_item = self.db.get_next_queue_item()
        if next_item:
            self.start_download.emit(next_item)
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
        else:
            QMessageBox.information(self, translation_manager.tr("dialogs.titles.info"), translation_manager.tr("queue.status.no_pending"))
    
    def pause_queue(self):
        """Kuyruğu duraklat"""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        # Kuyruk modunu kapat
        self.queue_paused.emit()  # Ana pencereye duraklatıldığını bildir
    
    def clear_all(self):
        """Tüm kuyruğu temizle"""
        count = self.db.clear_all_queue()
        self.load_queue()
        QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"), translation_manager.tr("queue.messages.items_cleared").format(count))
    
    def clear_selected(self):
        """Seçili öğeleri temizle"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, translation_manager.tr("dialogs.titles.warning"), translation_manager.tr("queue.errors.no_selection"))
            return
        
        # Seçili öğeleri sil
        for row in selected_rows:
            item_data = self.table.item(row, 0).data(Qt.UserRole)
            if item_data:
                self.db.remove_from_queue(item_data['id'])
        
        self.load_queue()
        QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"), translation_manager.tr("queue.messages.selected_cleared").format(len(selected_rows)))
    
    def clear_completed(self):
        """Tamamlananları temizle"""
        count = self.db.clear_queue('completed')
        self.db.reorder_queue_positions()
        self.load_queue()
        QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"), translation_manager.tr("queue.messages.completed_cleared").format(count))
    
    def clear_failed(self):
        """Başarısız indirmeleri temizle"""
        count = self.db.clear_queue('failed')
        self.db.reorder_queue_positions()
        self.load_queue()
        QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"), translation_manager.tr("queue.messages.failed_cleared").format(count))
    
    def clear_canceled(self):
        """Iptal edilmiş indirmeleri temizle"""
        # canceled ve paused durumlarını temizle
        count = self.db.clear_queue('canceled')
        count += self.db.clear_queue('paused')
        self.db.reorder_queue_positions()
        self.load_queue()
        QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"), translation_manager.tr("queue.messages.canceled_cleared").format(count))
    
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
        self.db.remove_from_queue(item_id)
        self.load_queue()
        self.queue_updated.emit()
    
    def show_context_menu(self, position):
        """Sağ tık menüsü göster"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        menu = QMenu()
        
        # Seçili öğelerin ID'lerini al
        selected_ids = []
        for row in selected_rows:
            item_data = self.table.item(row, 0).data(Qt.UserRole)
            if item_data:
                selected_ids.append(item_data['id'])
        
        # Menü öğeleri
        if len(selected_ids) == 1:
            # Tek seçim için menü
            item_id = selected_ids[0]
            
            download_now_action = menu.addAction(translation_manager.tr("queue.menu.download_now"))
            download_now_action.setIcon(icon_manager.get_icon("download", "#1976D2"))
            download_now_action.triggered.connect(lambda: self.download_now(item_id))
            
            menu.addSeparator()
            
            retry_action = menu.addAction(translation_manager.tr("queue.menu.retry"))
            retry_action.setIcon(icon_manager.get_icon("refresh-cw", "#FFA500"))
            retry_action.triggered.connect(lambda: self.retry_item(item_id))
            
            priority_menu = menu.addMenu(translation_manager.tr("queue.menu.priority"))
            priority_menu.setIcon(icon_manager.get_icon("star", "#9C27B0"))
            high_priority = priority_menu.addAction(translation_manager.tr("queue.priority.high"))
            high_priority.triggered.connect(lambda: self.set_priority(item_id, 2))
            
            normal_priority = priority_menu.addAction(translation_manager.tr("queue.priority.normal"))
            normal_priority.triggered.connect(lambda: self.set_priority(item_id, 1))
            
            low_priority = priority_menu.addAction(translation_manager.tr("queue.priority.low"))
            low_priority.triggered.connect(lambda: self.set_priority(item_id, 0))
            
            menu.addSeparator()
            
            delete_action = menu.addAction(translation_manager.tr("history.buttons.delete"))
            delete_action.setIcon(icon_manager.get_icon("trash-2", "#DC3545"))
            delete_action.triggered.connect(lambda: self.delete_item(item_id))
        else:
            # Çoklu seçim için menü
            download_selected_action = menu.addAction(translation_manager.tr("queue.menu.download_selected") + f" ({len(selected_ids)} {translation_manager.tr('queue.menu.item' if len(selected_ids) == 1 else 'queue.menu.items')})")
            download_selected_action.setIcon(icon_manager.get_icon("download", "#1976D2"))
            download_selected_action.triggered.connect(lambda: self.download_selected(selected_ids))
            
            menu.addSeparator()
            
            delete_selected_action = menu.addAction(translation_manager.tr("history.buttons.delete") + f" ({len(selected_ids)} {translation_manager.tr('queue.menu.item' if len(selected_ids) == 1 else 'queue.menu.items')})")
            delete_selected_action.setIcon(icon_manager.get_icon("trash-2", "#DC3545"))
            delete_selected_action.triggered.connect(lambda: self.delete_selected(selected_ids))
        
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
        
        # Create stats label if it doesn't exist
        if not hasattr(self, 'stats_label'):
            self.stats_label = QLabel()
            
        stats_text = "{} {} | {} {} | {} {}".format(
            translation_manager.tr("main.labels.total"), total,
            translation_manager.tr("main.labels.waiting"), pending,
            translation_manager.tr("main.labels.completed"), completed
        )
        self.stats_label.setText(stats_text)
    
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
    
    def download_now(self, item_id):
        """Tek öğeyi hemen indir"""
        # Önce veritabanından öğeyi al
        items = self.db.get_queue_items()
        queue_item = next((item for item in items if item['id'] == item_id), None)
        
        if queue_item and queue_item['status'] in ['pending', 'failed', 'queued']:
            # Spesifik indirme olduğunu işaretle
            queue_item['is_specific'] = True
            # İndirme sinyali gönder
            self.start_download.emit(queue_item)
    
    def download_selected(self, item_ids):
        """Seçili öğeleri sırayla indir"""
        # Veritabanından öğeleri al
        items = self.db.get_queue_items()
        
        # İndirilebilir öğeleri filtrele
        for item_id in item_ids:
            queue_item = next((item for item in items if item['id'] == item_id), None)
            if queue_item and queue_item['status'] in ['pending', 'failed', 'queued']:
                # Spesifik indirme olduğunu işaretle
                queue_item['is_specific'] = True
                # Her birini ayrı ayrı indir sinyali gönder
                self.start_download.emit(queue_item)
    
    def delete_selected(self, item_ids):
        """Seçili öğeleri sil"""
        for item_id in item_ids:
            self.db.remove_from_queue(item_id)
        self.load_queue()
        self.queue_updated.emit()
    
    def search_queue(self, text):
        """Kuyrukta arama yap"""
        # Arama metni boşsa normal yükle
        if not text.strip():
            self.load_queue()
            return
        
        # Arama sonuçlarını filtrele ve yükle
        self.load_queue()
    
    def mousePressEvent(self, a0: QMouseEvent):
        """Mouse tıklaması olduğunda"""
        # Tıklanan widget'ı kontrol et
        widget = self.childAt(a0.pos())
        
        # Eğer tablo dışında bir yere tıklandıysa seçimi temizle
        if widget != self.table and not self.table.isAncestorOf(widget):
            self.table.clearSelection()
        
        # Normal event işlemeye devam et
        super().mousePressEvent(a0)
    
    def closeEvent(self, event):
        """Widget kapatılırken temizlik yap"""
        # Timer'ı durdur
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        event.accept()
    
    def retranslateUi(self):
        """UI metinlerini yeniden çevir"""
        # Başlık
        if hasattr(self, 'title_label'):
            self.title_label.setText(translation_manager.tr("queue.title"))
        
        # Arama ve filtre label'ları
        if hasattr(self, 'search_label'):
            self.search_label.setText(translation_manager.tr("queue.labels.search"))
        if hasattr(self, 'filter_label'):
            self.filter_label.setText(translation_manager.tr("queue.labels.filter"))
        
        # Tablo başlıkları
        self.table.setHorizontalHeaderLabels([
            translation_manager.tr("queue.columns.title"), translation_manager.tr("queue.columns.status"), 
            translation_manager.tr("queue.columns.added"), translation_manager.tr("queue.columns.action")
        ])
        
        # Butonlar
        self.start_button.setText(translation_manager.tr("queue.buttons.resume_all"))
        self.start_button.setToolTip(translation_manager.tr("queue.tooltips.start_queue"))
        self.pause_button.setText(translation_manager.tr("queue.buttons.pause_all"))
        self.pause_button.setToolTip(translation_manager.tr("queue.tooltips.pause_queue"))
        self.clear_button.setText(translation_manager.tr("queue.buttons.clear_all"))
        self.clear_button.setToolTip(translation_manager.tr("queue.tooltips.clear_options"))
        
        # Arama ve filtre
        self.search_input.setPlaceholderText(translation_manager.tr("queue.placeholders.search"))
        
        # Filtre combobox'ı yeniden doldur - mevcut veriyi sakla
        current_data = self.status_filter.currentData()
        self.status_filter.clear()
        self.status_filter.addItem(translation_manager.tr("queue.filters.all"), None)
        self.status_filter.addItem(translation_manager.tr("queue.status.waiting"), "pending")
        self.status_filter.addItem(translation_manager.tr("queue.status.downloading"), "downloading")
        self.status_filter.addItem(translation_manager.tr("queue.status.completed"), "completed")
        self.status_filter.addItem(translation_manager.tr("queue.status.failed"), "failed")
        # Önceki seçimi geri yükle (data ile)
        for i in range(self.status_filter.count()):
            if self.status_filter.itemData(i) == current_data:
                self.status_filter.setCurrentIndex(i)
                break
        
        # Clear menü action'larını güncelle
        if hasattr(self, 'clear_all_action'):
            self.clear_all_action.setText(translation_manager.tr("queue.buttons.clear_all"))
        if hasattr(self, 'clear_selected_action'):
            self.clear_selected_action.setText(translation_manager.tr("queue.menu.clear_selected"))
        if hasattr(self, 'clear_completed_action'):
            self.clear_completed_action.setText(translation_manager.tr("queue.menu.clear_completed"))
        if hasattr(self, 'clear_failed_action'):
            self.clear_failed_action.setText(translation_manager.tr("queue.menu.clear_failed"))
        if hasattr(self, 'clear_canceled_action'):
            self.clear_canceled_action.setText(translation_manager.tr("queue.menu.clear_canceled"))
        
        # Tabloyu yeniden yükle
        self.load_queue()
        
        # İstatistikleri güncelle
        self.update_statistics()