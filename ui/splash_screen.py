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
        self.resize(700, 500)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Grid layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        
        # Kutular için listeler
        self.boxes = []
        self.box_animations = []
        
        # 8x8 grid oluştur
        self.grid_size = 8
        for row in range(self.grid_size):
            box_row = []
            for col in range(self.grid_size):
                box = QWidget()
                box.setFixedSize(QSize(60, 60))
                box.setStyleSheet("""
                    background-color: rgba(0, 0, 0, 80);
                    border-radius: 5px;
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
        
        # Başlık
        title_widget = QWidget()
        title_widget.setFixedHeight(150)
        title_layout = QVBoxLayout(title_widget)
        
        self.title_label = QLabel("MP3 YAP")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 48, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: white;")
        
        self.subtitle_label = QLabel("YouTube MP3 İndirici")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 18)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 180);")
        
        self.status_label = QLabel("Başlatılıyor...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont("Arial", 12)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 150);")
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        title_layout.addWidget(self.status_label)
        
        # Developer info
        dev_label = QLabel("Mehmet Yerli • mehmetyerli.com")
        dev_label.setAlignment(Qt.AlignCenter)
        dev_font = QFont("Arial", 10)
        dev_label.setFont(dev_font)
        dev_label.setStyleSheet("color: rgba(255, 255, 255, 120);")
        
        # Layout'ları birleştir
        main_layout.addStretch()
        main_layout.addLayout(self.grid_layout)
        main_layout.addWidget(title_widget)
        main_layout.addWidget(dev_label)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Arka plan rengi
        self.setStyleSheet("""
            SplashScreen {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2E7D32,
                    stop: 0.5 #1976D2,
                    stop: 1 #6A1B9A
                );
            }
        """)
        
        # Animasyon değişkenleri
        self.current_animation_index = 0
        self.animation_timer = None
        self.color_animation_timer = None
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        
        # Kutuları fade in yap
        self.animate_boxes_fade_in()
        
        # Durum mesajlarını güncelle
        QTimer.singleShot(500, lambda: self.status_label.setText("Modüller yükleniyor..."))
        QTimer.singleShot(1000, lambda: self.status_label.setText("Ayarlar kontrol ediliyor..."))
        QTimer.singleShot(1500, lambda: self.status_label.setText("Veritabanı hazırlanıyor..."))
        QTimer.singleShot(2000, lambda: self.status_label.setText("Arayüz oluşturuluyor..."))
        
        # Renk animasyonunu başlat
        QTimer.singleShot(800, self.start_color_wave_animation)
        
        # 3 saniye sonra kapat
        QTimer.singleShot(3000, self.animate_boxes_fade_out)
        
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
        """Dalga şeklinde renk animasyonu"""
        self.wave_position = 0
        
        def update_wave():
            colors = [
                "rgba(76, 175, 80, 180)",   # Yeşil
                "rgba(33, 150, 243, 180)",  # Mavi
                "rgba(156, 39, 176, 180)",  # Mor
                "rgba(255, 193, 7, 180)",   # Sarı
                "rgba(255, 87, 34, 180)",   # Turuncu
            ]
            
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    # Dalga efekti için mesafe hesapla
                    distance = abs(row + col - self.wave_position)
                    if distance < 3:
                        color_index = distance % len(colors)
                        self.boxes[row][col].setStyleSheet(f"""
                            background-color: {colors[color_index]};
                            border-radius: 5px;
                        """)
                    else:
                        self.boxes[row][col].setStyleSheet("""
                            background-color: rgba(0, 0, 0, 80);
                            border-radius: 5px;
                        """)
            
            self.wave_position += 1
            if self.wave_position > self.grid_size * 2 + 6:
                self.wave_position = 0
                
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(update_wave)
        self.color_animation_timer.start(100)  # Her 100ms'de güncelle
        
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