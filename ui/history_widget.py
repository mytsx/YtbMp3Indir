from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                            QHeaderView, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QThread
from PyQt5.QtGui import QDesktopServices
from database.manager import DatabaseManager
from datetime import datetime
from styles import style_manager
from utils.icon_manager import icon_manager
from utils.translation_manager import translation_manager


class HistoryWidget(QWidget):
    """İndirme geçmişi widget'ı"""
    
    # Dosyayı tekrar indir sinyali
    redownload_signal = pyqtSignal(str)  # URL
    # Kuyruğa ekleme sinyali
    add_to_queue_signal = pyqtSignal(list)  # URL listesi
    # İndir sekmesine ekleme sinyali
    add_to_download_signal = pyqtSignal(list)  # URL listesi
    
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
        
        self.search_label = QLabel(translation_manager.tr("Search:"))
        search_layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translation_manager.tr("Search in title or channel name..."))
        self.search_input.textChanged.connect(self.search_history)
        search_layout.addWidget(self.search_input)
        
        self.refresh_button = QPushButton(translation_manager.tr("Refresh"))
        self.refresh_button.setIcon(icon_manager.get_icon("refresh-cw", "#FFFFFF"))
        self.refresh_button.clicked.connect(self.load_history)
        style_manager.apply_button_style(self.refresh_button, "secondary")
        search_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton(translation_manager.tr("Clear History"))
        self.clear_button.setIcon(icon_manager.get_icon("trash-2", "#FFFFFF"))
        self.clear_button.clicked.connect(self.clear_history)
        style_manager.apply_button_style(self.clear_button, "danger")
        search_layout.addWidget(self.clear_button)
        
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            translation_manager.tr("Date"), translation_manager.tr("Title"), translation_manager.tr("Channel"), 
            translation_manager.tr("Format"), translation_manager.tr("Size"), translation_manager.tr("Actions")
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
        
        # Sağ tık menüsü
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
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
        loading_item = QTableWidgetItem(translation_manager.tr("Loading..."))
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
            date_item = QTableWidgetItem(date_str)
            # Record ID'yi sakla - bu kritik!
            date_item.setData(Qt.UserRole, record['id'])
            self.table.setItem(row_position, 0, date_item)
            
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
            browser_btn.setIcon(icon_manager.get_icon("external-link", "#FFFFFF"))
            browser_btn.setToolTip(translation_manager.tr("Open in Browser"))
            browser_btn.setFixedSize(24, 24)
            browser_btn.setObjectName("browserIconButton")
            browser_btn.clicked.connect(lambda checked, url=record['url']: self.open_in_browser(url))
            actions_layout.addWidget(browser_btn)
            
            # Tekrar indir butonu
            redownload_btn = QPushButton()
            redownload_btn.setIcon(icon_manager.get_icon("refresh-cw", "#FFFFFF"))
            redownload_btn.setToolTip(translation_manager.tr("Download Again"))
            redownload_btn.setFixedSize(24, 24)
            redownload_btn.setObjectName("redownloadIconButton")
            redownload_btn.clicked.connect(lambda checked, url=record['url']: self.redownload(url))
            actions_layout.addWidget(redownload_btn)
            
            # Sil butonu
            delete_btn = QPushButton()
            delete_btn.setIcon(icon_manager.get_icon("x", "#FFFFFF"))
            delete_btn.setToolTip(translation_manager.tr("Delete from History"))
            delete_btn.setFixedSize(24, 24)
            delete_btn.setObjectName("deleteIconButton")
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
        
        stats_text = translation_manager.tr(
            "Total: {} files | Size: {:.1f} MB | Today: {} files"
        ).format(stats['total_downloads'], stats['total_size_mb'], stats['today_downloads'])
        
        self.stats_label.setText(stats_text)
    
    def redownload(self, url):
        """URL'yi tekrar indir"""
        self.redownload_signal.emit(url)
    
    def open_in_browser(self, url):
        """URL'yi tarayıcıda aç"""
        QDesktopServices.openUrl(QUrl(url))
    
    def delete_record(self, record_id):
        """Kaydı sil"""
        if self.db_manager.delete_download(record_id):
            self.load_history()
    
    def clear_history(self):
        """Tüm geçmişi temizle"""
        count = self.db_manager.clear_history()
        QMessageBox.information(self, translation_manager.tr("Success"), translation_manager.tr("{} records deleted.").format(count))
        self.load_history()
    
    def add_selected_to_queue_action(self):
        """Seçili öğeleri kuyruğa ekle"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, translation_manager.tr("Warning"), translation_manager.tr("Please select videos to add to queue."))
            return
        
        # Seçili satırlardan record ID'lerini topla
        record_ids = []
        for row in selected_rows:
            item = self.table.item(row, 0)  # Tarih sütunu
            if item:
                record_id = item.data(Qt.UserRole)
                if record_id is not None:
                    record_ids.append(record_id)
        
        if not record_ids:
            return
        
        # Toplu olarak kayıtları getir
        downloads = self.db_manager.get_downloads_by_ids(record_ids)
        urls = [d['url'] for d in downloads if d and d.get('url')]
        
        # Duplicate URL'leri kaldır
        unique_urls = list(dict.fromkeys(urls))  # Sırayı koruyarak unique yap
        
        if unique_urls:
            self.add_to_queue_signal.emit(unique_urls)
            # Başarı mesajı ana pencerede gösterilecek
    
    def add_all_to_queue_action(self):
        """Tüm geçmişi kuyruğa ekle"""
        # Tüm geçmişteki URL'leri al
        history = self.db_manager.get_all_downloads()
        urls = [item['url'] for item in history if item.get('url')]
        
        # Duplicate URL'leri kaldır
        unique_urls = list(dict.fromkeys(urls))  # Sırayı koruyarak unique yap
        
        if not unique_urls:
            QMessageBox.warning(self, translation_manager.tr("Warning"), translation_manager.tr("No videos found in history to add."))
            return
        
        self.add_to_queue_signal.emit(unique_urls)
        QMessageBox.information(self, translation_manager.tr("Success"), translation_manager.tr("{} videos added to queue.").format(len(unique_urls)))
    
    def add_selected_to_download_action(self):
        """Seçili öğeleri indir sekmesine ekle"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, translation_manager.tr("Warning"), translation_manager.tr("Please select videos to add to download tab."))
            return
        
        # Seçili satırlardan record ID'lerini topla
        record_ids = []
        for row in selected_rows:
            item = self.table.item(row, 0)  # Tarih sütunu
            if item:
                record_id = item.data(Qt.UserRole)
                if record_id is not None:
                    record_ids.append(record_id)
        
        if not record_ids:
            return
        
        # Toplu olarak kayıtları getir
        downloads = self.db_manager.get_downloads_by_ids(record_ids)
        urls = [d['url'] for d in downloads if d and d.get('url')]
        
        # Duplicate URL'leri kaldır
        unique_urls = list(dict.fromkeys(urls))  # Sırayı koruyarak unique yap
        
        if unique_urls:
            self.add_to_download_signal.emit(unique_urls)
            # Başarı mesajı ana pencerede gösterilecek
    
    def show_context_menu(self, position):
        """Sağ tık menüsünü göster"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        menu = QMenu()
        
        # Seçilileri kuyruğa ekle
        add_to_queue_action = menu.addAction(translation_manager.tr("Add Selected to Queue"))
        add_to_queue_action.setIcon(icon_manager.get_icon("list", "#1976D2"))
        add_to_queue_action.triggered.connect(self.add_selected_to_queue_action)
        
        # Seçilileri indir sekmesine ekle
        add_to_download_action = menu.addAction(translation_manager.tr("Add Selected to Download Tab"))
        add_to_download_action.setIcon(icon_manager.get_icon("download", "#4CAF50"))
        add_to_download_action.triggered.connect(self.add_selected_to_download_action)
        
        menu.addSeparator()
        
        # Seçilileri sil
        delete_action = menu.addAction(translation_manager.tr("Delete Selected"))
        delete_action.setIcon(icon_manager.get_icon("trash-2", "#DC3545"))
        delete_action.triggered.connect(self.delete_selected)
        
        menu.exec_(self.table.mapToGlobal(position))
    
    def redownload_selected(self):
        """Seçili öğeleri yeniden indir"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if selected_rows:
            # İlk seçili satırın URL'sini al ve indir
            first_row = min(selected_rows)
            item = self.table.item(first_row, 0)
            if item:
                record_id = item.data(Qt.UserRole)
                download = self.db_manager.get_download_by_id(record_id)
                if download and download.get('url'):
                    self.redownload_signal.emit(download['url'])
    
    def delete_selected(self):
        """Seçili öğeleri sil"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        # Record ID'lerini topla
        record_ids = []
        for row in selected_rows:
            item = self.table.item(row, 0)
            if item:
                record_id = item.data(Qt.UserRole)
                if record_id is not None:
                    record_ids.append(record_id)
        
        if record_ids:
            # Toplu silme işlemi
            deleted_count = self.db_manager.delete_downloads_batch(record_ids)
            self.load_history()
            QMessageBox.information(self, translation_manager.tr("Success"), translation_manager.tr("{} records deleted.").format(deleted_count))
    
    def mousePressEvent(self, a0):
        """Mouse tıklaması olduğunda"""
        # Tıklanan widget'ı kontrol et
        widget = self.childAt(a0.pos())
        
        # Eğer tablo dışında bir yere tıklandıysa seçimi temizle
        if widget != self.table and not self.table.isAncestorOf(widget):
            self.table.clearSelection()
        
        # Normal event işlemeye devam et
        super().mousePressEvent(a0)
    
    def retranslateUi(self):
        """UI metinlerini yeniden çevir"""
        self.table.setHorizontalHeaderLabels([
            translation_manager.tr("Date"), translation_manager.tr("Title"), translation_manager.tr("Channel"), 
            translation_manager.tr("Format"), translation_manager.tr("Size"), translation_manager.tr("Actions")
        ])
        # Arama label ve placeholder güncelle
        if hasattr(self, 'search_label'):
            self.search_label.setText(translation_manager.tr("Search:"))
        self.search_input.setPlaceholderText(translation_manager.tr("Search in title or channel name..."))
        
        # Butonları güncelle
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(translation_manager.tr("Refresh"))
            self.refresh_button.setToolTip(translation_manager.tr("Refresh history"))
        if hasattr(self, 'clear_button'):
            self.clear_button.setText(translation_manager.tr("Clear History"))
            self.clear_button.setToolTip(translation_manager.tr("Clear all history"))
        
        # İstatistikleri güncelle - tabloyu yeniden yükle
        self.load_history()