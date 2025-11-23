"""
Modern Music Player Widget using macOS afplay
Compact, elegant music player for playing downloaded MP3 files
"""
import os
import logging
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                            QLabel, QSlider, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QProcess
from utils.icon_manager import icon_manager
from utils.translation_manager import translation_manager

logger = logging.getLogger(__name__)


class MusicPlayerWidget(QFrame):
    """
    Compact music player widget with play/pause/stop controls
    """

    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_file = None
        self.is_playing = False
        self.process = None
        self.start_time = 0
        self.duration = 0

        # Timer for updating elapsed time
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_time_display)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Create the player UI"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # Top row: Track info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)

        # Music icon
        music_icon = QLabel("🎵")
        music_icon.setStyleSheet("font-size: 16px;")
        info_layout.addWidget(music_icon)

        # Track name
        self.track_label = QLabel("Çalmaya hazır - Müzik seçmek için geçmişten bir dosyaya çift tıklayın")
        self.track_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        info_layout.addWidget(self.track_label, 1)

        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setIcon(icon_manager.get_icon("x", "#9ca3af"))
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setToolTip("Oynatıcıyı kapat")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
            }
        """)
        info_layout.addWidget(self.close_btn)

        main_layout.addLayout(info_layout)

        # Bottom row: Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        # Play button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(icon_manager.get_icon("play", "#FFFFFF"))
        self.play_pause_btn.setFixedSize(36, 36)
        self.play_pause_btn.setToolTip("Oynat")
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
            }
        """)
        controls_layout.addWidget(self.play_pause_btn)

        # Stop button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(icon_manager.get_icon("square", "#FFFFFF"))
        self.stop_btn.setFixedSize(36, 36)
        self.stop_btn.setToolTip("Durdur")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        controls_layout.addWidget(self.stop_btn)

        # Time display
        self.time_label = QLabel("0:00")
        self.time_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 13px;
                font-weight: 500;
                min-width: 70px;
                padding: 0 8px;
            }
        """)
        controls_layout.addWidget(self.time_label)

        # Status
        self.status_label = QLabel("⏸ Hazır")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 12px;
                background-color: #f3f4f6;
                padding: 4px 12px;
                border-radius: 12px;
            }
        """)
        controls_layout.addWidget(self.status_label)

        # Spacer
        controls_layout.addStretch(1)

        # Volume icon
        volume_icon = QLabel()
        volume_icon.setPixmap(icon_manager.get_icon("volume-2", "#6b7280").pixmap(18, 18))
        controls_layout.addWidget(volume_icon)

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(120)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #e5e7eb;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3b82f6;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
                border: 2px solid white;
            }
            QSlider::handle:horizontal:hover {
                background: #2563eb;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 2px;
            }
        """)
        controls_layout.addWidget(self.volume_slider)

        # Volume percentage
        self.volume_label = QLabel("70%")
        self.volume_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 11px;
                min-width: 35px;
            }
        """)
        controls_layout.addWidget(self.volume_label)

        main_layout.addLayout(controls_layout)

        # Widget frame style
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """)

        self.setLayout(main_layout)

    def setup_connections(self):
        """Connect signals"""
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.stop_btn.clicked.connect(self.stop_playback)
        self.close_btn.clicked.connect(self.close_player)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

    def on_volume_changed(self, value):
        """Volume slider changed"""
        self.volume_label.setText(f"{value}%")
        self.set_volume(value)

    def play_file(self, file_path):
        """Play a music file"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        try:
            logger.info(f"Playing file: {file_path}")

            # Stop current playback if any
            if self.is_playing:
                self.stop_playback()

            self.current_file = file_path

            # Set track name
            track_name = os.path.basename(file_path)
            # Remove .mp3 extension and video ID
            if track_name.endswith('.mp3'):
                track_name = track_name[:-4]
            # Remove [VIDEO_ID] pattern
            import re
            track_name = re.sub(r'\s*\[[^\]]+\]\s*$', '', track_name)

            self.track_label.setText(f"🎵 {track_name}")

            # Convert to absolute path
            abs_path = os.path.abspath(file_path)

            if not os.path.exists(abs_path):
                logger.error(f"File does not exist: {abs_path}")
                self.status_label.setText("❌ Dosya bulunamadı")
                return False

            # Clean up old process
            if self.process:
                try:
                    self.process.finished.disconnect()
                    self.process.kill()
                    self.process.waitForFinished(100)
                    self.process.deleteLater()
                except:
                    pass
                self.process = None

            # Create QProcess for afplay
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.on_process_output)
            self.process.readyReadStandardError.connect(self.on_process_error)
            self.process.errorOccurred.connect(self.on_process_error_occurred)
            self.process.finished.connect(self.on_playback_finished)

            # Calculate volume
            volume = self.volume_slider.value() / 100.0

            # Start playback
            logger.debug(f"Starting afplay with volume {volume}")
            self.process.start("afplay", ["-v", str(volume), abs_path])

            if not self.process.waitForStarted(2000):
                error = self.process.errorString()
                logger.error(f"Failed to start afplay: {error}")
                self.status_label.setText("❌ Başlatılamadı")
                return False

            logger.info(f"✅ afplay started, PID: {self.process.processId()}")

            self.is_playing = True
            self.status_label.setText("▶ Çalıyor")
            self.start_time = 0

            # Get duration
            try:
                import subprocess
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', abs_path],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    self.duration = int(float(result.stdout.strip()))
            except:
                self.duration = 0

            # Start timer
            self.timer.start()

            # Update UI
            self.play_pause_btn.setIcon(icon_manager.get_icon("pause", "#FFFFFF"))
            self.play_pause_btn.setToolTip("Duraklat")
            self.play_pause_btn.setEnabled(False)  # afplay doesn't support pause

            return True

        except Exception as e:
            logger.exception(f"Error playing file: {e}")
            self.status_label.setText("❌ Hata")
            return False

    def toggle_play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.stop_playback()
        elif self.current_file:
            self.play_file(self.current_file)

    def stop_playback(self):
        """Stop playback"""
        try:
            if self.process:
                try:
                    if self.process.state() == QProcess.Running:
                        self.process.terminate()
                        if not self.process.waitForFinished(500):
                            self.process.kill()
                except RuntimeError:
                    # Process already deleted
                    pass

            self.is_playing = False
            self.timer.stop()

            if hasattr(self, 'status_label'):
                self.status_label.setText("⏹ Durduruldu")
            if hasattr(self, 'time_label'):
                self.time_label.setText("0:00")

            self.start_time = 0
            self.duration = 0

            if hasattr(self, 'play_pause_btn'):
                self.play_pause_btn.setIcon(icon_manager.get_icon("play", "#FFFFFF"))
                self.play_pause_btn.setToolTip("Oynat")
                self.play_pause_btn.setEnabled(True)

        except Exception as e:
            logger.debug(f"Error stopping (ignored): {e}")

    def update_time_display(self):
        """Update time display"""
        try:
            if not self.is_playing:
                return

            self.start_time += 0.5

            mins = int(self.start_time // 60)
            secs = int(self.start_time % 60)

            if hasattr(self, 'time_label'):
                if self.duration > 0:
                    total_mins = self.duration // 60
                    total_secs = self.duration % 60
                    self.time_label.setText(f"{mins}:{secs:02d} / {total_mins}:{total_secs:02d}")
                else:
                    self.time_label.setText(f"{mins}:{secs:02d}")
        except RuntimeError:
            # Widget already deleted
            pass

    def on_process_output(self):
        """Handle output"""
        try:
            if self.process:
                output = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
                if output.strip():
                    logger.debug(f"afplay: {output.strip()}")
        except RuntimeError:
            # Process already deleted
            pass

    def on_process_error(self):
        """Handle error output"""
        try:
            if self.process:
                error = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')
                if error.strip():
                    logger.error(f"afplay error: {error.strip()}")
        except RuntimeError:
            # Process already deleted
            pass

    def on_process_error_occurred(self, error):
        """Handle QProcess errors"""
        try:
            error_string = self.process.errorString() if self.process else "Unknown"
            logger.error(f"Process error: {error}, {error_string}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"❌ Hata")
            self.is_playing = False
        except RuntimeError:
            # Process already deleted, ignore
            pass

    def on_playback_finished(self, exit_code, exit_status):
        """Playback finished"""
        try:
            logger.info(f"Finished: code={exit_code}, status={exit_status}")

            if hasattr(self, 'timer'):
                self.timer.stop()
            self.is_playing = False

            if hasattr(self, 'status_label'):
                if exit_code != 0:
                    self.status_label.setText(f"❌ Hata")
                else:
                    self.status_label.setText("✅ Tamamlandı")

            if hasattr(self, 'play_pause_btn'):
                self.play_pause_btn.setIcon(icon_manager.get_icon("play", "#FFFFFF"))
                self.play_pause_btn.setToolTip("Oynat")
                self.play_pause_btn.setEnabled(True)
        except RuntimeError:
            # Widget already deleted during cleanup
            pass

    def close_player(self):
        """Close player"""
        self.stop_playback()
        self.closed.emit()
        self.hide()

    def set_volume(self, value):
        """Set volume"""
        if self.is_playing and self.current_file:
            logger.debug(f"Restarting with volume {value}%")
            self.play_file(self.current_file)

    def closeEvent(self, event):
        """Cleanup"""
        try:
            # Stop timer first
            if hasattr(self, 'timer'):
                self.timer.stop()

            # Clean up process
            if self.process:
                try:
                    # Disconnect all signals first to avoid RuntimeError
                    self.process.readyReadStandardOutput.disconnect()
                    self.process.readyReadStandardError.disconnect()
                    self.process.errorOccurred.disconnect()
                    self.process.finished.disconnect()
                except:
                    pass

                # Kill process
                try:
                    if self.process.state() == QProcess.Running:
                        self.process.terminate()
                        if not self.process.waitForFinished(500):
                            self.process.kill()
                            self.process.waitForFinished(100)
                except:
                    pass

                self.process = None

            self.is_playing = False
        except Exception as e:
            logger.debug(f"Cleanup error (ignored): {e}")

        super().closeEvent(event)
