from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QLabel, 
                            QGraphicsOpacityEffect, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui import QFont
import random


class SplashScreen(QWidget):
    """Sadece kutulardan oluşan minimal splash screen"""
    
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları - tamamen şeffaf
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
        self.grid_layout.setSpacing(10)
        
        # Kutular için liste
        self.boxes = []
        self.box_animations = []
        
        # 8x8 grid
        self.grid_size = 8
        box_size = 50
        
        for row in range(self.grid_size):
            box_row = []
            for col in range(self.grid_size):
                # Tüm kutular aynı
                box = QWidget()
                box.setFixedSize(QSize(box_size, box_size))
                box.setStyleSheet("""
                    background-color: rgba(0, 0, 0, 80);
                    border-radius: 0px;
                """)
                
                self.grid_layout.addWidget(box, row, col)
                box_row.append(box)
                
                # Opacity efekti
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0)
                box.setGraphicsEffect(opacity_effect)
                
                # Animasyon
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
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        
        # Kutuları animasyonla göster
        self.animate_boxes_fade_in()
        
        # Renk dalgası animasyonu
        QTimer.singleShot(800, self.start_color_wave_animation)
        
        # 3 saniye sonra kapat
        QTimer.singleShot(3000, self.animate_boxes_fade_out)
    
    def update_status(self, message):
        """Durum mesajını güncelle"""
        self.status_label.setText(message)
        
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
        """Matematiksel formülle renk animasyonu"""
        self.time_step = 0
        self.fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        self.golden_ratio = 1.618033988749895
        
        def update_colors():
            import math
            
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    box = self.boxes[row][col]
                    
                    # Her kutu için benzersiz değer
                    box_id = row * self.grid_size + col
                    
                    # Fibonacci modülasyonu
                    fib_index = box_id % len(self.fibonacci)
                    fib_value = self.fibonacci[fib_index]
                    
                    # Altın oran ile açı hesaplama
                    angle = (box_id * self.golden_ratio * self.time_step) % 360
                    
                    # Mandelbrot benzeri fraktal formül
                    x = (col - self.grid_size/2) / (self.grid_size/4)
                    y = (row - self.grid_size/2) / (self.grid_size/4)
                    z = math.sqrt(x*x + y*y)
                    
                    # Sin ve cos ile periyodik değişim
                    r = int(127 + 127 * math.sin(angle * math.pi / 180 + fib_value * 0.1))
                    g = int(127 + 127 * math.cos(angle * math.pi / 180 + z * 2))
                    b = int(127 + 127 * math.sin((angle + 120) * math.pi / 180 + self.time_step * 0.1))
                    
                    # Renkleri sınırla
                    r = max(50, min(255, r))
                    g = max(50, min(255, g))
                    b = max(50, min(255, b))
                    
                    # Opacity için de matematiksel formül
                    opacity = int(100 + 80 * math.sin(self.time_step * 0.05 + box_id * 0.1))
                    opacity = max(80, min(200, opacity))
                    
                    box.setStyleSheet(f"""
                        background-color: rgba({r}, {g}, {b}, {opacity});
                        border-radius: 0px;
                    """)
            
            self.time_step += 1
                
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(update_colors)
        self.color_animation_timer.start(50)  # Her 50ms'de güncelle
        
    def animate_boxes_fade_out(self):
        """Kutuları fade out yap ve pencereyi kapat"""
        if self.color_animation_timer:
            self.color_animation_timer.stop()
            
        self.current_animation_index = 0
        
        def hide_next_box():
            if self.current_animation_index < len(self.box_animations):
                animation = self.box_animations[self.current_animation_index]
                animation.setStartValue(1)
                animation.setEndValue(0)
                animation.start()
                self.current_animation_index += 1
            else:
                self.animation_timer.stop()
                QTimer.singleShot(300, self.close_splash)
                
        # Animasyonları tekrar karıştır
        random.shuffle(self.box_animations)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(hide_next_box)
        self.animation_timer.start(10)  # Daha hızlı kapat
        
    def close_splash(self):
        """Splash screen'i kapat"""
        self.close()
        self.finished.emit()