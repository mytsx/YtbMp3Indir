import os
import re
import threading
import logging
from typing import List, Dict, Any
import yt_dlp
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QPushButton,
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                            QProgressBar, QMessageBox, QMenuBar, QMenu,
                            QAction, QTabWidget, QApplication, QShortcut,
                            QDialog, QDialogButtonBox)
from PyQt5.QtGui import QDesktopServices, QIcon, QKeySequence
from PyQt5.QtCore import QUrl, QTimer, QThread, pyqtSignal, Qt
from core.downloader import Downloader, DownloadSignals
from ui.settings_dialog import SettingsDialog
from ui.history_widget import HistoryWidget
from ui.queue_widget import QueueWidget
from ui.converter_widget import ConverterWidget
from ui.preloader_widget import PreloaderWidget
from utils.config import Config
from database.manager import DatabaseManager
from styles import style_manager
from utils.icon_manager import icon_manager
from utils.platform_utils import get_keyboard_icon, get_modifier_symbol, convert_shortcut_for_platform
from utils.update_checker import UpdateChecker
from utils.translation_manager import translation_manager
from services.url_analyzer import UrlAnalysisWorker, UrlAnalysisResult, UrlAnalyzer
from version import __version__, __app_name__, __author__

logger = logging.getLogger(__name__)

# Status message detection constants
STATUS_SYMBOLS = {"WARNING": "UYARI:", "SUCCESS": "✅", "ERROR": "❌"}
STATUS_KEYWORDS = {"QUEUED": "kuyrukta", "ADDED": "eklendi", "FAILED": "eklenemedi"}


class QueueProcessThread(QThread):
    """Background thread for processing URLs and adding to queue

    Fetches video metadata using yt-dlp and performs duplicate checking
    before adding videos to the download queue. Handles both individual
    videos and playlists.
    """
    finished_signal = pyqtSignal(int, list)  # added_count, duplicate_videos

    def __init__(self, urls: List[str], db_manager: DatabaseManager) -> None:
        """Initialize queue processing thread

        Args:
            urls: List of YouTube video or playlist URLs to process
            db_manager: Database manager instance for queue operations
        """
        super().__init__()
        self.urls = urls
        self.db_manager = db_manager

    def run(self) -> None:
        """Process URLs and add to queue

        Extracts metadata from URLs using yt-dlp, checks for duplicates
        against existing queue items, and performs batch insertion.
        Emits finished_signal with count and duplicate list when complete.

        Always emits finished_signal even on error for proper UI cleanup.
        """
        # Initialize variables for proper cleanup
        items_to_add = []
        duplicate_videos = []

        try:
            # yt-dlp seçenekleri
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
                'ignoreerrors': True,
                'skip_download': True,
            }

            # Mevcut video ID'lerini al
            existing_video_ids = self.db_manager.get_existing_queue_video_ids()

            for url in self.urls:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            if info.get('_type') == 'playlist':
                                # Playlist ise her video için kontrol et
                                playlist_title = info.get('title', 'İsimsiz Liste')
                                entries = info.get('entries', [])
                                for idx, entry in enumerate(entries):
                                    video_id = entry.get('id')
                                    video_url = entry.get('url', '')
                                    video_title = entry.get('title', f'Video {idx+1}')
                                    full_title = f"[{playlist_title}] {video_title}"

                                    # Duplicate kontrolü
                                    if video_id and video_id in existing_video_ids:
                                        duplicate_videos.append(video_title)
                                    else:
                                        items_to_add.append({
                                            'url': video_url,
                                            'video_title': full_title,
                                            'video_id': video_id
                                        })
                                        if video_id:
                                            existing_video_ids.add(video_id)
                            else:
                                # Tek video
                                video_id = info.get('id')
                                video_title = info.get('title', 'İsimsiz Video')

                                # Duplicate kontrolü
                                if video_id and video_id in existing_video_ids:
                                    duplicate_videos.append(video_title)
                                else:
                                    items_to_add.append({
                                        'url': url,
                                        'video_title': video_title,
                                        'video_id': video_id
                                    })
                except Exception as e:
                    logger.warning(f"Failed to fetch video info: {e}")
                    # Hata durumunda URL ile ekle
                    items_to_add.append({
                        'url': url,
                        'video_title': None,
                        'video_id': None
                    })

            # Toplu ekleme yap
            added_count = self.db_manager.add_to_queue_batch(items_to_add)

        except Exception as e:
            logger.error(f"Queue processing error: {e}")
            # Use partial results even on error
            added_count = self.db_manager.add_to_queue_batch(items_to_add) if items_to_add else 0

        finally:
            # MEDIUM #4: Always emit finished signal for proper cleanup
            # Even on error/cancellation, UI needs to know processing is done
            if 'added_count' not in locals():
                added_count = 0
            self.finished_signal.emit(added_count, duplicate_videos)


class MP3YapMainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translation_manager.tr("main.window.title"))
        self.setGeometry(100, 100, 1000, 700)
        
        # Set window icon if it exists
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Apply global stylesheet
        self.setStyleSheet(style_manager.get_combined_stylesheet())
        
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
        
        # URL kontrol cache (maksimum boyut sınırı ile)
        self.url_cache = {}  # URL -> info dict
        self.last_checked_urls = set()  # Son kontrol edilen URL'ler
        self.MAX_CACHE_SIZE = self.config.get('max_cache_size', 500)  # Ayarlardan al, yoksa 500
        self.url_analysis_worker = None  # Background URL analysis worker
        
        # Özel indirme listesi (sadece seçilenler için)
        self.selected_download_queue = []  # Sadece seçili öğeleri indirmek için
        self.is_queue_mode = False  # Normal kuyruk modu mu yoksa spesifik indirme mi
        self.current_queue_item = None  # Şu anda işlenen kuyruk öğesi
        
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
        
        # Klavye kısayollarını kur
        self.setup_keyboard_shortcuts()
        
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
        
        # Connect to language change signal for decoupled UI updates
        translation_manager.languageChanged.connect(self.on_language_changed)
        
        # Güncelleme kontrolü başlat
        self.check_for_updates()
    
    def setup_menu(self):
        """Menü çubuğunu oluştur"""
        menubar = self.menuBar()
        # macOS'ta native menubar sorun çıkarabiliyor
        menubar.setNativeMenuBar(False)
        
        # Dosya menüsü
        self.file_menu = menubar.addMenu(translation_manager.tr("main.menu.file"))
        
        # URL'leri içe aktar
        self.import_action = QAction(translation_manager.tr("main.menu.import_urls"), self)
        self.import_action.setShortcut('Ctrl+I')
        self.import_action.triggered.connect(self.import_urls)
        self.file_menu.addAction(self.import_action)
        
        self.file_menu.addSeparator()
        
        # Çıkış
        self.exit_action = QAction(translation_manager.tr("main.menu.exit"), self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # Araçlar menüsü (macOS'ta "Ayarlar" ismi sorun çıkarabiliyor)
        self.settings_menu = menubar.addMenu(translation_manager.tr("main.menu.tools"))
        
        # Tercihler/Ayarlar
        self.pref_action = QAction(translation_manager.tr("main.menu.settings_ellipsis"), self)
        self.pref_action.setShortcut('Ctrl+,')
        self.pref_action.triggered.connect(self.show_settings)
        self.settings_menu.addAction(self.pref_action)
        
        # Yardım menüsü
        self.help_menu = menubar.addMenu(translation_manager.tr("main.menu.help"))
        
        # Hakkında
        self.about_action = QAction(translation_manager.tr("main.menu.about"), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana widget olarak tab widget kullan
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)  # Tabları üstte ortala
        
        # İndirme sekmesi
        download_tab = self.create_download_tab()
        self.tab_widget.addTab(download_tab, translation_manager.tr("main.buttons.download_action"))
        
        # Geçmiş sekmesi
        self.history_widget = HistoryWidget()
        self.history_widget.redownload_signal.connect(self.add_url_to_download)
        self.history_widget.add_to_queue_signal.connect(self.add_urls_to_queue)
        self.history_widget.add_to_download_signal.connect(self.add_urls_to_download_tab)
        self.tab_widget.addTab(self.history_widget, translation_manager.tr("main.tabs.history"))
        
        # Tab değişikliğini dinle
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Kuyruk sekmesi
        self.queue_widget = QueueWidget()
        self.queue_widget.start_download.connect(self.process_queue_item)
        self.queue_widget.queue_started.connect(lambda: setattr(self, 'is_queue_mode', True))
        self.queue_widget.queue_paused.connect(self.on_queue_paused)
        self.tab_widget.addTab(self.queue_widget, translation_manager.tr("main.tabs.queue"))
        
        # MP3'e Dönüştür sekmesi
        self.converter_widget = ConverterWidget()
        self.tab_widget.addTab(self.converter_widget, translation_manager.tr("main.tabs.convert"))
        
        # Tab bar'ı ortalamak için
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setExpanding(False)
        
        # Tab widget styling is handled by base.qss
        
        # Ana widget olarak tab widget'ı ayarla
        self.setCentralWidget(self.tab_widget)
        
        # Durum çubuğu
        self.setup_status_bar()
    
    def setup_status_bar(self):
        """Durum çubuğunu ayarla"""
        status_bar = self.statusBar()
        
        # Sol taraf - genel durum mesajları için
        self.status_message = QLabel("")
        status_bar.addWidget(self.status_message)
        
        # Sağ taraf - kalıcı widget'lar
        # Güncelleme durumu
        self.update_status_widget = QPushButton()
        self.update_status_widget.setFlat(True)
        self.update_status_widget.setCursor(Qt.PointingHandCursor)
        self.update_status_widget.setObjectName("updateStatusButton")
        self.update_status_widget.hide()  # Başlangıçta gizli
        self.update_status_widget.clicked.connect(self.show_update_dialog)  # Signal'i burada bir kez bağla
        status_bar.addPermanentWidget(self.update_status_widget)
        
        # Versiyon etiketi (güncelleme kontrolü yapılmadan önce)
        self.version_label = QLabel(f"v{__version__}")
        self.version_label.setObjectName("versionLabel")
        status_bar.addPermanentWidget(self.version_label)
        
        # Klavye kısayolları butonu
        self.shortcuts_hint = QPushButton(translation_manager.tr("main.tooltips.shortcuts_f1"))
        # Tema'ya göre renk belirle
        theme = self.config.get('theme', 'light')
        icon_color = style_manager.colors.DARK_TEXT_SECONDARY if theme == 'dark' else style_manager.colors.TEXT_SECONDARY
        # Platform'a göre ikon seç
        keyboard_icon = get_keyboard_icon()
        # Windows için keyboard ikonu kullan (windows.svg yoksa)
        if keyboard_icon == "windows" and not icon_manager.has_icon("windows"):
            keyboard_icon = "keyboard"
        self.shortcuts_hint.setIcon(icon_manager.get_icon(keyboard_icon, icon_color))
        self.shortcuts_hint.setFlat(True)
        self.shortcuts_hint.setCursor(Qt.PointingHandCursor)
        self.shortcuts_hint.clicked.connect(self.show_shortcuts_help)
        self.shortcuts_hint.setToolTip(translation_manager.tr("main.tooltips.show_shortcuts"))
        self.shortcuts_hint.setObjectName("statusBarButton")
        self.shortcuts_hint.setMaximumWidth(140)  # Genişlik arttırıldı
        
        status_bar.addPermanentWidget(self.shortcuts_hint)
    
    def create_download_tab(self):
        """İndirme sekmesini oluştur"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # URL giriş alanı
        self.url_label = QLabel(translation_manager.tr("main.labels.paste_urls"))
        self.url_text = QTextEdit()
        self.url_text.setToolTip(translation_manager.tr("main.tooltips.paste_urls"))
        
        # Durum ve ilerleme
        status_layout = QHBoxLayout()
        self.status_label = QLabel(translation_manager.tr("main.status.ready"))
        self.status_label.setMinimumHeight(30)
        self.status_label.setObjectName("downloadStatus")
        status_layout.addWidget(self.status_label)
        
        # İndirme ilerleme çubuğu
        progress_layout = QHBoxLayout()
        self.current_file_label = QLabel(translation_manager.tr("main.labels.file"))
        self.progress_bar = QProgressBar()
        self.progress_percent = QLabel("0%")
        self.progress_percent.setObjectName("progressPercent")
        progress_layout.addWidget(self.current_file_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_percent)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.download_button = QPushButton(translation_manager.tr("main.buttons.download_action"))
        self.download_button.setIcon(icon_manager.get_icon("download", "#FFFFFF"))
        self.download_button.clicked.connect(self.start_download)  # type: ignore
        self.download_button.setToolTip(translation_manager.tr("main.tooltips.start_download"))
        style_manager.apply_button_style(self.download_button, "download")
        
        # İptal butonu
        self.cancel_button = QPushButton(translation_manager.tr("common.buttons.cancel"))
        self.cancel_button.setIcon(icon_manager.get_icon("x", "#FFFFFF"))
        self.cancel_button.clicked.connect(self.cancel_download)  # type: ignore
        self.cancel_button.setEnabled(False)
        self.cancel_button.setToolTip(translation_manager.tr("main.tooltips.cancel_download"))
        style_manager.apply_button_style(self.cancel_button, "danger")
        
        # Kuyruğa ekle butonu
        self.add_to_queue_button = QPushButton(translation_manager.tr("main.buttons.add_to_queue"))
        self.add_to_queue_button.setIcon(icon_manager.get_icon("plus", "#FFFFFF"))
        self.add_to_queue_button.clicked.connect(self.add_to_queue)  # type: ignore
        self.add_to_queue_button.setToolTip(translation_manager.tr("main.tooltips.add_to_queue"))
        style_manager.apply_button_style(self.add_to_queue_button, "secondary")
        
        # Temizle butonu
        self.clear_button = QPushButton(translation_manager.tr("main.buttons.clear"))
        self.clear_button.setIcon(icon_manager.get_icon("trash-2", "#FFFFFF"))
        self.clear_button.clicked.connect(self.clear_urls)  # type: ignore
        self.clear_button.setToolTip(translation_manager.tr("main.tooltips.clear_urls"))
        style_manager.apply_button_style(self.clear_button, "warning")
        
        # Klasörü aç butonu
        self.open_folder_button = QPushButton(translation_manager.tr("history.buttons.open_folder"))
        self.open_folder_button.setIcon(icon_manager.get_icon("folder", "#FFFFFF"))
        self.open_folder_button.clicked.connect(self.open_output_folder)  # type: ignore
        self.open_folder_button.setToolTip(translation_manager.tr("main.tooltips.open_folder"))
        style_manager.apply_button_style(self.open_folder_button, "accent")
        
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
        self.url_status_bar.setObjectName("urlStatusBar")  # Base object name for consistent base styling
        self.url_status_bar.setVisible(False)
        
        # Layout'a widget'ları ekle
        layout.addWidget(self.url_label)
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
        
        # Preloader widget
        self.preloader = PreloaderWidget(self)
        self.preloader.canceled.connect(self.cancel_current_operation)
        self.preloader.hide()
        
        widget.setLayout(layout)
        return widget
    
    def start_download(self):
        """İndirme işlemini başlat"""
        urls = self.url_text.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, translation_manager.tr("dialogs.titles.warning"), translation_manager.tr("main.errors.no_url"))
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
            QMessageBox.information(self, translation_manager.tr("dialogs.titles.info"), translation_manager.tr("main.status.no_downloads"))
    
    def show_settings(self):
        """Ayarlar penceresini göster"""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Ayarlar değişmiş olabilir, gerekli güncellemeleri yap
            pass
    
    def check_for_updates(self):
        """Güncelleme kontrolü başlat"""
        self.update_checker = UpdateChecker()
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.check_finished.connect(self.on_update_check_finished)
        self.update_checker.start()
    
    def on_update_available(self, update_info):
        """Güncelleme mevcut olduğunda"""
        self.latest_update_info = update_info
        
        # Güncelleme butonunu göster
        self.update_status_widget.setText(translation_manager.tr("main.status.update_available_version").format(update_info['version']))
        self.update_status_widget.show()
        
        # Versiyon etiketini gizle
        self.version_label.hide()
    
    def on_update_check_finished(self, success, message):
        """Güncelleme kontrolü tamamlandığında"""
        if not success and not hasattr(self, 'latest_update_info'):
            # Hata durumunda sadece log'la, kullanıcıyı rahatsız etme
            logging.warning(f"Update check: {message}")
    
    def show_update_dialog(self):
        """Güncelleme dialogunu göster"""
        if not hasattr(self, 'latest_update_info'):
            return
        
        info = self.latest_update_info
        
        dialog = QDialog(self)
        dialog.setWindowTitle(translation_manager.tr("dialogs.update.available"))
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel(f"<h2>{translation_manager.tr('dialogs.update.new_version')}: v{info['version']}</h2>")
        layout.addWidget(title)

        # Değişiklikler
        changes_label = QLabel(f"<b>{translation_manager.tr('dialogs.update.changes')}:</b>")
        layout.addWidget(changes_label)
        
        changes_text = QTextEdit()
        changes_text.setReadOnly(True)
        changes_text.setMarkdown(info['body'])
        layout.addWidget(changes_text)
        
        # Butonlar
        button_box = QDialogButtonBox()
        download_btn = button_box.addButton(translation_manager.tr("main.buttons.download_action"), QDialogButtonBox.AcceptRole)
        later_btn = button_box.addButton(translation_manager.tr("dialogs.update.later"), QDialogButtonBox.RejectRole)
        
        download_btn.clicked.connect(lambda: self.open_update_url(info['download_url']))
        later_btn.clicked.connect(dialog.reject)
        
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def open_update_url(self, url):
        """Güncelleme URL'sini aç"""
        QDesktopServices.openUrl(QUrl(url))
    
    def show_about(self):
        """Hakkında dialogunu göster"""
        QMessageBox.about(self, translation_manager.tr("dialogs.titles.about").format(__app_name__),
            f"<h3>{__app_name__}</h3>"
            f"<p>{translation_manager.tr('dialogs.about.version')} {__version__}</p>"
            f"<p>{translation_manager.tr('dialogs.about.description')}</p>"
            f"<p><b>{translation_manager.tr('dialogs.about.developer')}:</b> {__author__}</p>"
            f"<p><b>{translation_manager.tr('dialogs.about.web')}:</b> <a href='https://mehmetyerli.com'>mehmetyerli.com</a></p>"
            f"<p><b>{translation_manager.tr('dialogs.about.license')}:</b> {translation_manager.tr('dialogs.about.open_source')}</p>")
    
    def import_urls(self):
        """URL'leri metin dosyasından içe aktar"""
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            translation_manager.tr("dialogs.file.select_url_file"), 
            "", 
            translation_manager.tr("dialogs.file.text_files") + " (*.txt);;" + translation_manager.tr("dialogs.file.all_files") + " (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    urls = f.read()
                    self.url_text.setPlainText(urls)
                    QMessageBox.information(self, translation_manager.tr("dialogs.titles.success"),
                        translation_manager.tr("main.status.urls_loaded").format(len(urls.strip().split())))
            except (IOError, OSError) as e:
                QMessageBox.critical(self, translation_manager.tr("dialogs.titles.error"),
                    translation_manager.tr("main.errors.file_read").format(str(e)))
            except UnicodeDecodeError as e:
                QMessageBox.critical(self, translation_manager.tr("dialogs.titles.error"),
                    f"Dosya kodlama hatası: {str(e)}")
    
    def update_progress(self, filename, percent, text):
        """İlerleme çubuğunu güncelle"""
        # Playlist progress varsa vurgula
        if '[' in text and '/' in text:
            # Playlist progress içeriyor
            self.current_file_label.setText(translation_manager.tr("main.status.playlist_downloading").format(filename))
            style_manager.set_widget_property(self.progress_percent, "progressType", "playlist")
        else:
            self.current_file_label.setText(translation_manager.tr("main.labels.file_name").format(filename))
            style_manager.set_widget_property(self.progress_percent, "progressType", "file")
            
        if percent >= 0:
            self.progress_bar.setValue(int(percent))
            self.progress_bar.setRange(0, 100)
        else:
            self.progress_bar.setRange(0, 0)  # Belirsiz ilerleme
        self.progress_percent.setText(text)
    
    def download_finished(self, filename):
        """İndirme tamamlandığında çağrılır"""
        self.status_label.setText(translation_manager.tr("main.status.download_completed_file").format(filename))
    
    def download_error(self, filename, error):
        """İndirme hatası durumunda çağrılır"""
        self.status_label.setText(translation_manager.tr("main.errors.error_format").format(filename, error))
    
    def update_status(self, status):
        """Durum mesajını güncelle"""
        # Önemli uyarıları silme
        current_text = self.status_label.text()
        if any(x in current_text for x in STATUS_SYMBOLS.values()) and \
           any(x in current_text.lower() for x in STATUS_KEYWORDS.values()):
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
                style_manager.apply_status_style(self.status_label, "info", refresh=True)
        else:
            # Normal durum için stil sıfırla
            self.status_label.setObjectName("downloadStatus")
        
        # Eğer tüm indirmeler tamamlandıysa butonları güncelle
        completed_msg = translation_manager.tr("main.status.all_downloads_completed")
        stopped_msg = translation_manager.tr("main.status.download_stopped")
        if status == completed_msg or status == stopped_msg:
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            # Geçmiş sekmesini güncelle
            if hasattr(self, 'history_widget'):
                self.history_widget.load_history()
            # İndirme tamamlandıysa URL'leri temizle
            if status == completed_msg:
                self.url_text.clear()
                self.url_status_bar.setVisible(False)
    
    def add_url_to_download(self, url):
        """Geçmişten URL'yi indirme listesine ekle"""
        # İndirme sekmesine geç
        self.tab_widget.setCurrentIndex(0)
        
        # Mevcut URL'leri kontrol et
        current_text = self.url_text.toPlainText().strip()
        if current_text:
            existing_urls = set(line.strip() for line in current_text.split('\n') if line.strip())
            if url not in existing_urls:
                self.url_text.setPlainText(current_text + '\n' + url)
                self.status_label.setText(translation_manager.tr("main.status.url_added_download_tab"))
                style_manager.apply_alert_style(self.status_label, "success")
            # Zaten varsa sessizce geç
        else:
            self.url_text.setPlainText(url)
            self.status_label.setText(translation_manager.tr("main.status.url_added_to_download_tab"))
            style_manager.apply_alert_style(self.status_label, "success")
    
    def add_urls_to_queue(self, urls):
        """Birden fazla URL'yi kuyruğa ekle (Geçmiş sekmesinden)"""
        # URL'leri text widget'a yaz ve add_to_queue'u çağır
        self.url_text.setPlainText('\n'.join(urls))
        self.add_to_queue()
    
    def add_urls_to_download_tab(self, urls):
        """Birden fazla URL'yi indir sekmesine ekle (Geçmiş sekmesinden)"""
        # İndir sekmesine geç
        self.tab_widget.setCurrentIndex(0)
        
        # Mevcut URL'leri al ve set'e çevir
        current_text = self.url_text.toPlainText().strip()
        existing_urls = set()
        if current_text:
            existing_urls = set(line.strip() for line in current_text.split('\n') if line.strip())
        
        # Yeni URL'leri filtrele (duplicate olmayanlar)
        new_urls = [url for url in urls if url not in existing_urls]
        
        if new_urls:
            # Sadece yeni URL'leri ekle
            if current_text:
                # Mevcut URL'ler varsa alt satıra ekle
                self.url_text.setPlainText(current_text + '\n' + '\n'.join(new_urls))
            else:
                # Boşsa direkt ekle
                self.url_text.setPlainText('\n'.join(new_urls))
            
            # Durum mesajı - sadece eklenen sayıyı göster
            self.status_label.setText(translation_manager.tr("main.status.videos_added_download_tab").format(len(new_urls)))
            style_manager.apply_alert_style(self.status_label, "success")
        else:
            # Hiç yeni URL yoksa sessizce geç, durum mesajı gösterme
            pass
    
    def add_to_queue(self):
        """URL'leri kuyruğa ekle"""
        urls = self.url_text.toPlainText().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            QMessageBox.warning(self, translation_manager.tr("dialogs.titles.warning"), translation_manager.tr("main.errors.no_url"))
            return
        
        # Preloader göster
        self.preloader.show_with_text(
            translation_manager.tr("main.status.fetching_info").format(len(urls)),
            cancelable=True
        )
        
        # Butonları devre dışı bırak
        self.add_to_queue_button.setEnabled(False)
        self.download_button.setEnabled(False)
        
        # Thread oluştur ve başlat
        self.queue_thread = QueueProcessThread(urls, self.db_manager)
        self.queue_thread.finished_signal.connect(self._on_queue_process_finished)
        self.queue_thread.start()
    
    def _on_queue_process_finished(self, added_count, duplicate_videos):
        """Kuyruk işleme thread'i tamamlandığında"""
        # Preloader'ı gizle
        self.preloader.hide_loader()
        
        # Butonları geri etkinleştir
        self.add_to_queue_button.setEnabled(True)
        self.download_button.setEnabled(True)
        style_manager.apply_alert_style(self.status_label, "info", refresh=False)  # Varsayılan stil
        
        # Sonuç mesajı göster
        total_urls = len(self.url_text.toPlainText().strip().split('\n'))
        duplicate_count = len(duplicate_videos)
        
        if added_count > 0 and duplicate_count == 0:
            self.status_label.setText(translation_manager.tr("queue.status.videos_added").format(added_count))
            style_manager.apply_alert_style(self.status_label, "success")
            self.url_text.clear()  # URL'leri temizle
            # Kuyruğu yenile
            self.queue_widget.load_queue()
            # Kuyruk sekmesine geç
            self.tab_widget.setCurrentIndex(2)
        elif added_count > 0 and duplicate_count > 0:
            self.status_label.setText(translation_manager.tr("queue.status.videos_added_some_exist").format(added_count, duplicate_count))
            style_manager.apply_alert_style(self.status_label, "warning")
            self.url_text.clear()  # URL'leri temizle
            self.queue_widget.load_queue()
            self.tab_widget.setCurrentIndex(2)
        elif duplicate_count > 0:
            # Sadece duplicate varsa
            self.status_label.setText(translation_manager.tr("queue.status.all_videos_exist").format(duplicate_count))
            style_manager.apply_alert_style(self.status_label, "warning")
        else:
            self.status_label.setText(translation_manager.tr("queue.errors.add_failed"))
            style_manager.apply_alert_style(self.status_label, "error")
    
    
    def process_queue_item(self, queue_item):
        """Kuyruktan gelen öğeyi işle"""
        # Eğer bu bir normal kuyruk başlatma değilse (spesifik indirme ise)
        # ve queue_item'da 'is_specific' işareti varsa, is_queue_mode'u kapat
        if queue_item.get('is_specific', False):
            self.is_queue_mode = False
        
        # Eğer başka bir indirme devam ediyorsa, bu öğeyi özel listeye ekle
        if self.current_queue_item is not None:
            if not self.is_queue_mode or queue_item.get('is_specific', False):
                # Spesifik indirme ise listeye ekle
                if queue_item not in self.selected_download_queue:
                    self.selected_download_queue.append(queue_item)
                    # Durumu "İndirilecek" olarak güncelle
                    self.queue_widget.update_download_status(queue_item['id'], 'queued')
            return
        
        # İndirme durumunu güncelle
        self.queue_widget.update_download_status(queue_item['id'], 'downloading')
        
        # Downloader'ı hazırla
        self.current_queue_item = queue_item
        
        # Sinyal bağlantılarını güncelle (kuyruk için)
        try:
            self.signals.finished.disconnect()
            self.signals.error.disconnect()
        except (TypeError, RuntimeError) as e:
            # Signal zaten disconnect veya hiç bağlı değil
            logger.debug(f"Signal disconnect ignored: {e}")
        
        self.signals.finished.connect(self.queue_download_finished)
        self.signals.error.connect(self.queue_download_error)

        # İndirmeyi başlat
        output_dir = self.config.get('output_path', 'music')
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
        if self.current_queue_item is not None:
            # Dönüştürme durumunu kontrol et
            if "MP3'e dönüştürülüyor" in status or "Dönüştürme" in status:
                self.queue_widget.update_download_status(
                    self.current_queue_item['id'], 'converting'
                )
    
    def queue_download_finished(self, filename):
        """Kuyruk indirmesi tamamlandığında"""
        if self.current_queue_item is not None:
            self.queue_widget.update_download_status(
                self.current_queue_item['id'], 'completed'
            )
            # Geçmişi güncelle
            if hasattr(self, 'history_widget'):
                self.history_widget.load_history()
            
            # Mevcut indirmeyi temizle
            self.current_queue_item = None
            
            # Özel listede bekleyen varsa onu başlat
            if self.selected_download_queue:
                next_item = self.selected_download_queue.pop(0)
                # Kısa bir gecikme ile sonrakini başlat
                QTimer.singleShot(500, lambda: self.process_queue_item(next_item))
            elif self.is_queue_mode:
                # Normal kuyruk modunda ise, bir sonraki öğeyi al
                QTimer.singleShot(500, lambda: self.queue_widget.start_queue())
    
    def queue_download_error(self, filename, error):
        """Kuyruk indirmesinde hata oluştuğunda"""
        if self.current_queue_item is not None:
            self.queue_widget.update_download_status(
                self.current_queue_item['id'], 'failed', error
            )
            
            # Mevcut indirmeyi temizle
            self.current_queue_item = None
            
            # Özel listede bekleyen varsa onu başlat
            if self.selected_download_queue:
                next_item = self.selected_download_queue.pop(0)
                # Kısa bir gecikme ile sonrakini başlat
                QTimer.singleShot(500, lambda: self.process_queue_item(next_item))
            elif self.is_queue_mode:
                # Normal kuyruk modunda ise, bir sonraki öğeyi al
                QTimer.singleShot(500, lambda: self.queue_widget.start_queue())
    
    def _add_to_cache(self, url, info):
        """Cache'e güvenli ekleme (boyut kontrolü ile)"""
        if len(self.url_cache) >= self.MAX_CACHE_SIZE:
            # En eski girişi kaldır (FIFO)
            oldest_key = next(iter(self.url_cache))
            del self.url_cache[oldest_key]
        
        self.url_cache[url] = info
    
    def _trim_cache(self):
        """Trim cache to MAX_CACHE_SIZE if needed"""
        while len(self.url_cache) > self.MAX_CACHE_SIZE:
            # Remove oldest entry (FIFO)
            oldest_key = next(iter(self.url_cache))
            del self.url_cache[oldest_key]
    
    def on_queue_paused(self):
        """Kuyruk duraklatıldığında"""
        self.is_queue_mode = False
        # Özel indirme listesini de temizle
        self.selected_download_queue.clear()
        # "queued" durumundaki öğeleri "pending"e çevir
        items = self.queue_widget.db.get_queue_items()
        for item in items:
            if item['status'] == 'queued':
                self.queue_widget.db.update_queue_status(item['id'], 'pending')
        # Tabloyu yenile
        self.queue_widget.load_queue()
    
    def on_tab_changed(self, index):
        """Tab değiştiğinde çağrılır"""
        # Geçmiş sekmesi (index 1) seçildiyse yenile
        if index == 1 and hasattr(self, 'history_widget'):
            self.history_widget.load_history()
        
        # İndirme sekmesine (index 0) geri dönüldüğünde
        if index == 0:
            # Eğer URL alanı boşsa uyarıları temizle
            if not self.url_text.toPlainText().strip():
                self.status_label.clear()
                style_manager.apply_alert_style(self.status_label, "info", refresh=False)  # Varsayılan stil
                self.url_status_bar.setVisible(False)
    
    def cancel_download(self):
        """İndirmeyi iptal et"""
        # Downloader'ı durdur
        if hasattr(self, 'downloader'):
            self.downloader.stop()
        
        # Butonları güncelle
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_label.setText(translation_manager.tr("main.status.download_cancelled"))
            
    def clear_urls(self):
        """URL metin alanını temizle"""
        self.url_text.clear()
        self.status_label.setText(translation_manager.tr("main.status.urls_cleared"))
        style_manager.apply_alert_style(self.status_label, "success")
        self.url_status_bar.setVisible(False)
    
    def on_url_text_changed(self):
        """URL metni değiştiğinde"""
        # Eğer duplicate uyarısı varsa timer'ı başlatma
        current_text = self.status_label.text()
        if STATUS_KEYWORDS["QUEUED"] in current_text.lower() and STATUS_SYMBOLS["WARNING"] in current_text:
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
        
        # Cancel any existing analysis
        if self.url_analysis_worker and self.url_analysis_worker.isRunning():
            self.url_analysis_worker.cancel()
            self.url_analysis_worker.wait()
        
        # Start background analysis
        self.url_analysis_worker = UrlAnalysisWorker(
            urls, self.db_manager, self.config.to_dict(), self.url_cache, self
        )
        
        # Connect signals
        self.url_analysis_worker.started.connect(self.on_url_analysis_started)
        self.url_analysis_worker.progress.connect(self.on_url_analysis_progress)
        self.url_analysis_worker.finished.connect(self.on_url_analysis_finished)
        self.url_analysis_worker.error.connect(self.on_url_analysis_error)
        
        # Start analysis
        self.url_analysis_worker.start()
    
    def on_url_analysis_started(self):
        """URL analysis started"""
        self.url_status_bar.setText(translation_manager.tr("⏳ URL'ler kontrol ediliyor..."))
        style_manager.set_widget_property(self.url_status_bar, "statusType", "warning")
        self.url_status_bar.setVisible(True)
    
    def on_url_analysis_progress(self, message: str):
        """URL analysis progress update"""
        self.url_status_bar.setText(message)
        style_manager.set_widget_property(self.url_status_bar, "statusType", "info")
    
    def on_url_analysis_error(self, error_msg: str):
        """URL analysis error"""
        self.url_status_bar.setText(f"❌ {error_msg}")
        style_manager.set_widget_property(self.url_status_bar, "statusType", "error")
    
    def on_url_analysis_finished(self, result: UrlAnalysisResult):
        """URL analysis finished - display results"""
        status_parts = []
        
        # Valid URLs and playlist info
        if result.valid_urls:
            playlists = [p for p in result.playlist_info if p.get('video_count', 1) > 1]
            single_videos = [p for p in result.playlist_info if p.get('video_count', 1) == 1]
            
            if result.total_videos == len(result.valid_urls):
                # Only single videos
                status_parts.append(f"✓ {len(result.valid_urls)} video indirmeye hazır")
            else:
                # Mixed (playlists + videos)
                parts = []
                if playlists:
                    parts.append(f"{len(playlists)} playlist")
                if single_videos:
                    parts.append(f"{len(single_videos)} video")
                status_parts.append(f"✓ {' ve '.join(parts)} (toplam {result.total_videos} video)")
                
                # Playlist details
                for p in playlists:
                    if p.get('title') and p['title'] not in ['Bilinmeyen', 'Tek Video']:
                        playlist_text = f"  • {p['title'][:30]}"
                        if len(p['title']) > 30:
                            playlist_text += "..."
                        playlist_text += f" ({p.get('video_count', 1)} video)"
                        status_parts.append(playlist_text)
        
        # Invalid URLs
        if result.invalid_urls:
            status_parts.append(f"✗ {len(result.invalid_urls)} geçersiz URL")
        
        # Database status
        if result.files_exist > 0:
            status_parts.append(f"✓ {result.files_exist} dosya hem indirilmiş hem de klasörde mevcut")
        
        if result.files_missing > 0:
            status_parts.append(f"⚠ {result.files_missing} dosya daha önce indirilmiş ama klasörde bulunamadı")
        
        if result.already_downloaded > result.files_exist + result.files_missing:
            unknown = result.already_downloaded - result.files_exist - result.files_missing
            status_parts.append(f"? {unknown} dosya kaydı eksik bilgi içeriyor")
        
        # Update status bar
        if status_parts:
            self.url_status_bar.setText(" | ".join(status_parts))
            self.url_status_bar.setVisible(True)
            
            # Set color based on priority
            if result.invalid_urls:
                style_manager.set_widget_property(self.url_status_bar, "statusType", "error")
            elif result.files_exist > 0 and result.files_missing == 0:
                style_manager.set_widget_property(self.url_status_bar, "statusType", "info")
            elif result.files_missing > 0:
                style_manager.set_widget_property(self.url_status_bar, "statusType", "warning")
            else:
                style_manager.set_widget_property(self.url_status_bar, "statusType", "success")
        else:
            self.url_status_bar.setVisible(False)
        
        # Update cache size limit
        self._trim_cache()
    
    def show_cached_url_status(self, urls):
        """Cache'den URL durumunu göster"""
        # Use UrlAnalyzer for consistency - avoid duplicate logic
        valid_urls, invalid_urls = UrlAnalyzer.validate_youtube_urls(urls)
        
        total_videos = 0
        playlists = []
        single_videos = []
        
        for url in valid_urls:
            # Cache'de var mı?
            if url in self.url_cache:
                info = self.url_cache[url]
                if info.get('is_playlist'):
                    playlists.append(info)
                    total_videos += info.get('video_count', 1)
                else:
                    single_videos.append(info)
                    total_videos += 1
            else:
                # Cache'de yok, tek video varsay
                single_videos.append({'title': 'Tek Video', 'video_count': 1})
                total_videos += 1
        
        # Durum mesajını oluştur
        if not valid_urls and not invalid_urls:
            self.url_status_bar.setVisible(False)
            return
            
        status_parts = []
        
        if total_videos > 0:
            if total_videos == len(valid_urls) and not playlists:
                # Sadece tek videolar var
                status_parts.append(translation_manager.tr("main.status.videos_ready").format(len(valid_urls)))
            else:
                # Karışık (playlist + tek video)
                parts = []
                if playlists:
                    parts.append(translation_manager.tr("main.labels.playlist_count").format(len(playlists)))
                if single_videos:
                    parts.append(translation_manager.tr("main.labels.video_count").format(len(single_videos)))
                status_parts.append(translation_manager.tr("main.status.playlist_ready").format(
                    translation_manager.tr("common.conjunction.and").join(parts), total_videos))
        
        if invalid_urls:
            status_parts.append(translation_manager.tr("main.status.invalid_urls_count").format(len(invalid_urls)))
        
        if status_parts:
            self.url_status_bar.setText(" | ".join(status_parts))
            # Renk ayarla
            if invalid_urls:
                # Kırmızı
                style_manager.set_widget_property(self.url_status_bar, "statusType", "error")
            else:
                # Yeşil
                style_manager.set_widget_property(self.url_status_bar, "statusType", "success")
            self.url_status_bar.setVisible(True)
        else:
            self.url_status_bar.setVisible(False)
    
    def get_keyboard_shortcuts(self):
        """Get keyboard shortcuts definition."""
        return [
            # Ana kısayollar
            {
                'key': QKeySequence.Paste,
                'description': 'URL yapıştır ve otomatik doğrula',
                'action': self.paste_and_validate_url,
                'category': 'main'
            },
            {
                'key': QKeySequence("Ctrl+Return"),
                'description': 'Hızlı indirme başlat',
                'action': self.quick_download,
                'category': 'main'
            },
            {
                'key': QKeySequence("Ctrl+D"),
                'description': 'İndirme klasörünü aç',
                'action': self.open_output_folder,
                'category': 'main'
            },
            {
                'key': QKeySequence("Ctrl+H"),
                'description': 'Geçmiş sekmesine geç',
                'action': lambda: self.tab_widget.setCurrentIndex(1),
                'category': 'navigation'
            },
            {
                'key': QKeySequence("Ctrl+K"),
                'description': 'Kuyruk sekmesine geç',
                'action': lambda: self.tab_widget.setCurrentIndex(2),
                'category': 'navigation'
            },
            {
                'key': QKeySequence.Refresh,
                'description': 'Mevcut sekmeyi yenile',
                'action': self.refresh_current_tab,
                'category': 'main'
            },
            {
                'key': QKeySequence.HelpContents,
                'description': 'Bu yardım penceresini göster',
                'action': self.show_shortcuts_help,
                'category': 'help'
            },
            {
                'key': QKeySequence("Escape"),
                'description': 'İndirmeyi iptal et',
                'action': self.handle_escape,
                'category': 'main'
            },
            {
                'key': QKeySequence("Ctrl+I"),
                'description': "URL'leri dosyadan içe aktar",
                'action': None,  # Menüde tanımlı
                'category': 'file'
            },
            {
                'key': QKeySequence("Ctrl+,"),
                'description': 'Tercihler/Ayarlar',
                'action': None,  # Menüde tanımlı
                'category': 'file'
            },
            {
                'key': QKeySequence("Ctrl+Q"),
                'description': 'Uygulamadan çık',
                'action': None,  # Menüde tanımlı
                'category': 'file'
            }
        ]
    
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        shortcuts = self.get_keyboard_shortcuts()
        
        for shortcut_def in shortcuts:
            if shortcut_def['action']:  # Eğer action tanımlıysa shortcut oluştur
                shortcut = QShortcut(shortcut_def['key'], self)
                shortcut.activated.connect(shortcut_def['action'])
    
    def paste_and_validate_url(self):
        """URL yapıştır ve otomatik doğrula"""
        # Sadece indirme sekmesindeyken çalışsın
        if self.tab_widget.currentIndex() == 0:
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text:
                # Mevcut metne ekle (yeni satırla)
                current_text = self.url_text.toPlainText()
                if current_text and not current_text.endswith('\n'):
                    text = '\n' + text
                cursor = self.url_text.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertText(text)
                # URL kontrolü otomatik tetiklenecek (textChanged sinyali ile)
    
    def quick_download(self):
        """Hızlı indirme başlat (Ctrl+Enter)"""
        # Sadece indirme sekmesindeyken ve URL varken çalışsın
        if self.tab_widget.currentIndex() == 0:
            if self.url_text.toPlainText().strip() and self.download_button.isEnabled():
                self.start_download()
    
    def refresh_current_tab(self):
        """Mevcut sekmeyi yenile (F5)"""
        current_index = self.tab_widget.currentIndex()
        if current_index == 1:  # Geçmiş sekmesi
            self.history_widget.load_history()
        elif current_index == 2:  # Kuyruk sekmesi
            self.queue_widget.load_queue()
        # Diğer sekmeler için özel yenileme yok
    
    def show_shortcuts_help(self):
        """Klavye kısayolları yardımını göster (F1)"""
        # Merkezi veri yapısından HTML oluştur
        shortcuts = self.get_keyboard_shortcuts()
        
        # Kategorilere göre grupla
        categories = {
            'main': {'title': translation_manager.tr("dialogs.shortcuts.main_title"), 'shortcuts': []},
            'navigation': {'title': translation_manager.tr("dialogs.shortcuts.navigation_title"), 'shortcuts': []},
            'file': {'title': translation_manager.tr("dialogs.shortcuts.file_ops_title"), 'shortcuts': []},
            'help': {'title': translation_manager.tr("main.menu.help"), 'shortcuts': []}
        }
        
        for shortcut in shortcuts:
            category = shortcut.get('category', 'main')
            if category in categories:
                categories[category]['shortcuts'].append(shortcut)
        
        # HTML oluştur
        html = f"<h3>{translation_manager.tr('main.menu.keyboard_shortcuts')}</h3>"
        
        for _, category_data in categories.items():
            if category_data['shortcuts']:
                html += f"<h4>{category_data['title']}</h4>"
                html += "<table>"
                
                for shortcut in category_data['shortcuts']:
                    # Kısayol tuşunu string'e çevir
                    key = shortcut['key']
                    if not isinstance(key, QKeySequence):
                        key = QKeySequence(key)
                    key_str = key.toString(QKeySequence.NativeText)
                    
                    # Açıklamaları çevir
                    desc = shortcut['description']
                    desc_translated = {
                        'URL yapıştır ve otomatik doğrula': translation_manager.tr("main.tooltips.paste_auto_validate"),
                        'Hızlı indirme başlat': translation_manager.tr("dialogs.shortcuts.quick_download"),
                        'İndirme klasörünü aç': translation_manager.tr("dialogs.shortcuts.open_folder"),
                        'Geçmiş sekmesine geç': translation_manager.tr("dialogs.shortcuts.switch_history"),
                        'Kuyruk sekmesine geç': translation_manager.tr("dialogs.shortcuts.switch_queue"),
                        'Mevcut sekmeyi yenile': translation_manager.tr("dialogs.shortcuts.refresh_tab"),
                        'Bu yardım penceresini göster': translation_manager.tr("dialogs.shortcuts.show_help"),
                        'İndirmeyi iptal et': translation_manager.tr("dialogs.shortcuts.cancel_download"),
                        "URL'leri dosyadan içe aktar": translation_manager.tr("main.menu.import_urls"),
                        'Tercihler/Ayarlar': translation_manager.tr("dialogs.shortcuts.preferences"),
                        'Uygulamadan çık': translation_manager.tr("dialogs.shortcuts.quit_app")
                    }.get(desc, desc)
                    
                    html += f"<tr><td><b>{key_str}</b></td><td>{desc_translated}</td></tr>"
                
                html += "</table>"
        
        # Kuyruk sekmesi kısayolları (widget içinde tanımlı)
        modifier = get_modifier_symbol()
        html += f"""
        <h4>{translation_manager.tr("dialogs.shortcuts.queue_title")}</h4>
        <table>
        <tr><td><b>{modifier}+A</b></td><td>{translation_manager.tr("dialogs.shortcuts.select_all")}</td></tr>
        <tr><td><b>Delete</b></td><td>{translation_manager.tr("dialogs.shortcuts.delete_selected")}</td></tr>
        <tr><td><b>Space</b></td><td>{translation_manager.tr("dialogs.shortcuts.pause_resume")}</td></tr>
        </table>
        """
        
        QMessageBox.information(self, translation_manager.tr("main.menu.keyboard_shortcuts"), html)
    
    def handle_escape(self):
        """Escape tuşu işlemi"""
        # İndirme devam ediyorsa iptal et
        if hasattr(self, 'downloader') and self.downloader.is_running:
            self.cancel_download()
        # Kuyruk indirmesi varsa iptal et
        elif self.current_queue_item is not None:
            self.queue_widget.pause_queue()
    
    def cancel_current_operation(self):
        """Mevcut işlemi iptal et"""
        # Preloader'dan gelen iptal işlemi
        pass  # Şu an için boş, gerektiğinde implement edilecek
    
    
    def closeEvent(self, a0):
        """Pencere kapatılırken"""
        # Aktif indirme varsa durdur
        if hasattr(self, 'downloader') and self.downloader.is_running:
            self.downloader.stop()
        # Pencereyi kapat
        a0.accept()
    
    def on_language_changed(self, lang_code):
        """Handle language change signal from translation manager"""
        self.retranslateUi()
        
        # Update tab titles
        self.tab_widget.setTabText(0, translation_manager.tr("main.buttons.download_action"))
        self.tab_widget.setTabText(1, translation_manager.tr("main.tabs.history"))
        self.tab_widget.setTabText(2, translation_manager.tr("main.tabs.queue"))
        self.tab_widget.setTabText(3, translation_manager.tr("main.tabs.convert"))
        
        # Update child widgets
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'retranslateUi'):
                widget.retranslateUi()
    
    def retranslateUi(self):
        """UI metinlerini yeniden çevir (dil değiştiğinde)"""
        # Ana pencere başlığı
        self.setWindowTitle(translation_manager.tr("main.window.title"))
        
        # Menü metinlerini güncelle (menüleri yeniden oluşturmadan)
        if hasattr(self, 'file_menu'):
            self.file_menu.setTitle(translation_manager.tr("main.menu.file"))
            self.import_action.setText(translation_manager.tr("main.menu.import_urls"))
            self.exit_action.setText(translation_manager.tr("main.menu.exit"))
        if hasattr(self, 'settings_menu'):
            self.settings_menu.setTitle(translation_manager.tr("main.menu.tools"))
            self.pref_action.setText(translation_manager.tr("main.menu.settings_ellipsis"))
        if hasattr(self, 'help_menu'):
            self.help_menu.setTitle(translation_manager.tr("main.menu.help"))
            self.about_action.setText(translation_manager.tr("main.menu.about"))
        
        # Status bar widget'larının metinlerini güncelle (yeniden oluşturmadan)
        if hasattr(self, 'shortcuts_hint'):
            self.shortcuts_hint.setText(translation_manager.tr("main.tooltips.shortcuts_f1"))
            self.shortcuts_hint.setToolTip(translation_manager.tr("main.tooltips.show_shortcuts"))
        
        # Tab başlıkları
        self.tab_widget.setTabText(0, translation_manager.tr("main.buttons.download_action"))
        self.tab_widget.setTabText(1, translation_manager.tr("main.tabs.history"))
        self.tab_widget.setTabText(2, translation_manager.tr("main.tabs.queue"))
        self.tab_widget.setTabText(3, translation_manager.tr("main.tabs.convert"))
        
        # Download tab'ındaki butonları güncelle
        if hasattr(self, 'download_button'):
            self.download_button.setText(translation_manager.tr("main.buttons.download_action"))
            self.download_button.setToolTip(translation_manager.tr("main.tooltips.start_download"))
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setText(translation_manager.tr("common.buttons.cancel"))
            self.cancel_button.setToolTip(translation_manager.tr("main.tooltips.cancel_download"))
        if hasattr(self, 'add_to_queue_button'):
            self.add_to_queue_button.setText(translation_manager.tr("main.buttons.add_to_queue"))
            self.add_to_queue_button.setToolTip(translation_manager.tr("main.tooltips.add_to_queue"))
        if hasattr(self, 'clear_button'):
            self.clear_button.setText(translation_manager.tr("main.buttons.clear"))
            self.clear_button.setToolTip(translation_manager.tr("main.tooltips.clear_urls"))
        if hasattr(self, 'open_folder_button'):
            self.open_folder_button.setText(translation_manager.tr("history.buttons.open_folder"))
            self.open_folder_button.setToolTip(translation_manager.tr("main.tooltips.open_folder"))
        
        # Label'ları güncelle
        if hasattr(self, 'status_label'):
            self.status_label.setText(translation_manager.tr("main.status.ready"))
        if hasattr(self, 'current_file_label'):
            self.current_file_label.setText(translation_manager.tr("main.labels.file"))
        
        # URL giriş alanı label ve tooltip güncelle
        if hasattr(self, 'url_label'):
            self.url_label.setText(translation_manager.tr("main.labels.paste_urls"))
        if hasattr(self, 'url_text'):
            self.url_text.setToolTip(translation_manager.tr("main.tooltips.paste_urls"))