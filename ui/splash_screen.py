from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QLabel, 
                            QGraphicsOpacityEffect, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor
import random


class SplashScreen(QWidget):
    """Kutularla animasyonlu açılış ekranı"""
    
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(600, 500)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 0)  # Alt margin 0
        main_layout.setSpacing(0)  # Grid ve status bar arasında boşluk olmasın
        
        # Grid container - şeffaf
        grid_container = QWidget()
        grid_container.setStyleSheet("background-color: transparent;")
        
        # Grid layout
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(3)
        
        # Kutular için listeler
        self.boxes = []
        self.box_animations = []
        
        # 10x10 grid oluştur - daha küçük kutular
        self.grid_size = 10
        box_size = 40
        
        for row in range(self.grid_size):
            box_row = []
            for col in range(self.grid_size):
                box = QWidget()
                box.setFixedSize(QSize(box_size, box_size))
                box.setStyleSheet("""
                    background-color: rgba(0, 0, 0, 80);
                    border-radius: 3px;
                """)
                self.grid_layout.addWidget(box, row, col)
                box_row.append(box)
                
                # Opacity efekti ekle
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0)
                box.setGraphicsEffect(opacity_effect)
                
                # Animasyon oluştur
                animation = QPropertyAnimation(opacity_effect, b"opacity")
                animation.setDuration(300)
                animation.setEasingCurve(QEasingCurve.InOutQuad)
                self.box_animations.append(animation)
                
            self.boxes.append(box_row)
        
        # Status bar widget - ince bar şeklinde
        self.status_widget = QWidget()
        self.status_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
            }
        """)
        self.status_widget.setFixedHeight(30)
        
        # Status label
        status_layout = QHBoxLayout(self.status_widget)
        status_layout.setContentsMargins(20, 0, 20, 0)
        
        self.status_label = QLabel("Başlatılıyor...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont("Arial", 11)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        
        # Ana layout'a ekle
        main_layout.addWidget(grid_container)
        main_layout.addWidget(self.status_widget)
        
        # Animasyon değişkenleri
        self.current_animation_index = 0
        self.animation_timer = None
        self.color_animation_timer = None
        
        # Uygulama hazır mı kontrolü için
        self.app_ready = False
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        
        # Kutuları fade in yap
        self.animate_boxes_fade_in()
        
        # Renk animasyonunu başlat
        QTimer.singleShot(800, self.start_color_wave_animation)
        
    def update_status(self, message):
        """Durum mesajını güncelle"""
        self.status_label.setText(message)
        
    def set_app_ready(self):
        """Uygulama hazır olduğunda çağrılır"""
        self.app_ready = True
        self.update_status("Hazır!")
        # Fade out yok - direkt kapat
        QTimer.singleShot(500, self.close_splash)
        
    def animate_boxes_fade_in(self):
        """Kutuları sırayla fade in yap"""
        def show_next_box():
            if self.current_animation_index < len(self.box_animations):
                # Random sırayla göster
                animation = self.box_animations[self.current_animation_index]
                animation.setStartValue(0)
                animation.setEndValue(1)
                animation.start()
                self.current_animation_index += 1
            else:
                self.animation_timer.stop()
                
        # Animasyonları karıştır
        random.shuffle(self.box_animations)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(show_next_box)
        self.animation_timer.start(20)  # Her 20ms'de bir kutu
        
    def start_color_wave_animation(self):
        """Dalga şeklinde renk animasyonu - rastgele noktadan başlar"""
        # Rastgele başlangıç noktası
        self.wave_center_x = random.randint(0, self.grid_size - 1)
        self.wave_center_y = random.randint(0, self.grid_size - 1)
        self.wave_radius = 0
        
        def update_wave():
            # Uygulama hazırsa animasyonu durdur
            if self.app_ready:
                return
            
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    # Merkeze olan mesafeyi hesapla
                    dx = col - self.wave_center_x
                    dy = row - self.wave_center_y
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    # Dalga içindeyse tamamen rastgele renk ver
                    if abs(distance - self.wave_radius) < 2:
                        # Tamamen rastgele RGB değerleri
                        r = random.randint(50, 255)
                        g = random.randint(50, 255)
                        b = random.randint(50, 255)
                        self.boxes[row][col].setStyleSheet(f"""
                            background-color: rgba({r}, {g}, {b}, 180);
                            border-radius: 3px;
                        """)
                    else:
                        self.boxes[row][col].setStyleSheet("""
                            background-color: rgba(0, 0, 0, 80);
                            border-radius: 3px;
                        """)
            
            self.wave_radius += 0.8  # Daha hızlı büyüsün
            # Dalga ekranı geçince yeni rastgele nokta seç
            if self.wave_radius > self.grid_size * 0.8:  # Daha kısa mesafede yenile
                self.wave_radius = 0
                self.wave_center_x = random.randint(0, self.grid_size - 1)
                self.wave_center_y = random.randint(0, self.grid_size - 1)
                
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(update_wave)
        self.color_animation_timer.start(50)  # Her 50ms'de güncelle - daha hızlı
        
        
    def close_splash(self):
        """Splash screen'i kapat"""
        self.close()
        self.finished.emit()