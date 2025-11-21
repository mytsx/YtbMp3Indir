"""Universal preloader widget for MP3Yap"""
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
import random


from utils.translation_manager import translation_manager

class PreloaderWidget(QWidget):
    """Evrensel preloader widget'ı"""
    
    # ESC tuşu ile iptal sinyali
    canceled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Modal olarak ayarla
        if parent:
            self.setWindowModality(Qt.ApplicationModal)
        
        # Tam ekran overlay
        if parent:
            self.setGeometry(parent.geometry())
        
        # Animasyon renkleri (splash screen'deki gibi)
        self.colors = [
            "#FF6B6B",  # Kırmızı
            "#4ECDC4",  # Turkuaz
            "#45B7D1",  # Mavi
            "#F9DC5C",  # Sarı
            "#95E1D3",  # Mint
            "#FA86C4"   # Pembe
        ]
        
        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Animasyon widget'ı
        self.animation_widget = AnimationWidget(self.colors)
        self.animation_widget.setFixedSize(180, 60)  # 6 kutu için
        
        # Açıklama metni
        self.description_label = QLabel(translation_manager.tr("status.processing"))
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 600;
                margin-top: 20px;
                background: transparent;
            }
        """)
        
        # ESC iptal bildirimi
        self.cancel_label = QLabel(translation_manager.tr("preloader.labels.cancel_hint"))
        self.cancel_label.setAlignment(Qt.AlignCenter)
        self.cancel_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                margin-top: 10px;
                background: transparent;
            }
        """)
        self.cancel_label.hide()  # Başlangıçta gizli
        
        layout.addWidget(self.animation_widget)
        layout.addWidget(self.description_label)
        layout.addWidget(self.cancel_label)
        
        self.setLayout(layout)
    
    def show_with_text(self, text: str, cancelable: bool = False):
        """
        Preloader'ı göster

        Args:
            text: Already translated text to display
                  (Callers should use translation_manager.tr() before passing)
            cancelable: Whether to show cancel instruction
        """
        # REFACTORED: Removed brittle heuristic detection
        # Now: Always expect already-translated text from caller
        # This makes the API more explicit and maintainable
        self.description_label.setText(text)
             
        if cancelable:
            self.cancel_label.show()
        else:
            self.cancel_label.hide()
        
        # Parent widget'ın üzerinde konumlan
        if self.parent():
            parent_rect = self.parent().rect()
            self.setGeometry(parent_rect)
        
        self.show()
        self.raise_()
        self.activateWindow()
        self.animation_widget.start_animation()
        QApplication.processEvents()
    
    def hide_loader(self):
        """Preloader'ı gizle"""
        self.animation_widget.stop_animation()
        self.hide()
    
    def paintEvent(self, event):
        """Arka plan çizimi"""
        _ = event  # Unused
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Yarı saydam siyah overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
    
    def keyPressEvent(self, event):
        """ESC tuşu kontrolü"""
        if event.key() == Qt.Key_Escape and self.cancel_label.isVisible():
            self.canceled.emit()
            self.hide_loader()


class AnimationWidget(QWidget):
    """6'lı kutu animasyonu"""
    
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.boxes = []
        self.animations = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        
        # 6 kutu oluştur
        for i in range(6):
            box = QWidget(self)
            box.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.colors[i]};
                    border-radius: 4px;
                }}
            """)
            box.setGeometry(i * 30, 20, 25, 25)
            self.boxes.append(box)
    
    def start_animation(self):
        """Animasyonu başlat"""
        self.timer.start(100)  # 100ms interval
        self.animate_boxes()
    
    def stop_animation(self):
        """Animasyonu durdur"""
        self.timer.stop()
        for animation in self.animations:
            animation.stop()
        self.animations.clear()
    
    def animate_boxes(self):
        """Kutuları animasyonla hareket ettir"""
        for i, box in enumerate(self.boxes):
            # Yukarı-aşağı animasyon
            animation = QPropertyAnimation(box, b"geometry")
            animation.setDuration(600)
            animation.setLoopCount(-1)  # Sonsuz döngü
            
            # Başlangıç ve bitiş pozisyonları
            start_rect = QRect(i * 30, 20, 25, 25)
            end_rect = QRect(i * 30, 5, 25, 25)
            
            animation.setStartValue(start_rect)
            animation.setEndValue(end_rect)
            
            # Gecikme için timer kullan
            QTimer.singleShot(i * 100, animation.start)
            
            self.animations.append(animation)
    
    def update_animation(self):
        """Renkleri rastgele değiştir"""
        for box in self.boxes:
            # Rastgele renk seç
            color = random.choice(self.colors)
            box.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)