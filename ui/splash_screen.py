from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QLabel, 
                            QGraphicsOpacityEffect, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QFont
import random


class SplashScreen(QWidget):
    """Basit rastgele kutu animasyonlu splash screen"""
    
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları - tamamen şeffaf
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(600, 500)
        
        # Ana layout kullanmayacağız, absolute positioning kullanacağız
        
        # Grid container - şeffaf
        self.grid_container = QWidget(self)
        self.grid_container.setStyleSheet("background-color: transparent;")
        self.grid_container.setGeometry(50, 50, 500, 400)  # Başlangıç pozisyonu
        
        # Grid layout
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Kutular için liste
        self.boxes = []
        self.box_animations = []
        
        # 16x16 grid - dengeli çözünürlük  
        self.grid_size = 16
        self.box_size = 25
        
        for row in range(self.grid_size):
            box_row = []
            for col in range(self.grid_size):
                # Tüm kutular aynı
                box = QWidget()
                box.setFixedSize(QSize(self.box_size, self.box_size))
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
                animation.setDuration(50)  # Çok hızlı fade in
                animation.setEasingCurve(QEasingCurve.InOutQuad)
                self.box_animations.append(animation)
                
            self.boxes.append(box_row)
        
        # Status bar widget - ince bar şeklinde
        self.status_widget = QWidget(self)
        self.status_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
            }
        """)
        self.status_widget.setGeometry(50, 450, 500, 30)  # Başlangıçta altta
        
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
        
        # Animasyon değişkenleri
        self.current_animation_index = 0
        self.animation_timer = None
        self.color_animation_timer = None
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        
        # Kutuları animasyonla göster
        self.animate_boxes_fade_in()
        
        # Rastgele kutu animasyonu
        QTimer.singleShot(300, self.start_random_animation)
    
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
        self.animation_timer.start(1)  # Her 1ms'de bir kutu - ultra hızlı
        
    def start_random_animation(self):
        """Basit rastgele kutu animasyonu"""
        self.update_status("Yükleniyor...")
        
        # Hangi satırların silindiğini takip et
        self.removed_rows = set()
        self.animation_count = 0
        # Her kutunun durumunu sakla
        self.box_states = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Başlangıçta tüm kutuları koyu yap
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                style = """
                    background-color: rgba(20, 20, 20, 100);
                    border-radius: 0px;
                """
                self.boxes[row][col].setStyleSheet(style)
                self.box_states[row][col] = style
        
        # Farklı renk paletleri
        color_palettes = [
            # Neon
            [(255, 0, 128), (0, 255, 255), (255, 255, 0), (128, 255, 0), (255, 0, 255)],
            # Pastel
            [(255, 182, 193), (176, 224, 230), (255, 218, 185), (221, 160, 221), (152, 251, 152)],
            # Canlı
            [(255, 69, 0), (50, 205, 50), (30, 144, 255), (255, 215, 0), (138, 43, 226)],
            # Soğuk
            [(70, 130, 180), (64, 224, 208), (72, 209, 204), (95, 158, 160), (176, 196, 222)],
            # Sıcak
            [(255, 99, 71), (255, 140, 0), (255, 165, 0), (255, 192, 203), (219, 112, 147)]
        ]
        
        # Rastgele bir palet seç
        current_palette = random.choice(color_palettes)
        
        def random_box_animation():
            nonlocal current_palette
            # Her frame'de rastgele birkaç kutu yak - sadece görünür satırlarda
            visible_rows = [r for r in range(self.grid_size) if r not in self.removed_rows]
            
            if visible_rows:
                for _ in range(5):  # Her seferinde 5 kutu - daha hızlı
                    row = random.choice(visible_rows)
                    col = random.randint(0, self.grid_size - 1)
                    
                    # Paletten rastgele renk seç ve varyasyon ekle
                    base_color = random.choice(current_palette)
                    # Renklere hafif varyasyon ekle
                    r = max(0, min(255, base_color[0] + random.randint(-30, 30)))
                    g = max(0, min(255, base_color[1] + random.randint(-30, 30)))
                    b = max(0, min(255, base_color[2] + random.randint(-30, 30)))
                    
                    style = f"""
                        background-color: rgba({r}, {g}, {b}, 200);
                        border-radius: 0px;
                    """
                    self.boxes[row][col].setStyleSheet(style)
                    self.box_states[row][col] = style
                
                # Bazı kutuları söndür
                for _ in range(3):  # Her seferinde 3 kutu söndür
                    row = random.choice(visible_rows)
                    col = random.randint(0, self.grid_size - 1)
                    
                    style = """
                        background-color: rgba(20, 20, 20, 100);
                        border-radius: 0px;
                    """
                    self.boxes[row][col].setStyleSheet(style)
                    self.box_states[row][col] = style
            
            # Bazen palet değiştir
            if random.random() < 0.05:  # %5 şansla
                current_palette = random.choice(color_palettes)
            
            # Her 3 frame'de bir satır sil - daha da hızlı
            self.animation_count += 1
            if self.animation_count % 3 == 0 and len(self.removed_rows) < self.grid_size - 1:
                # Rastgele bir satır seç
                available_rows = [r for r in range(self.grid_size) if r not in self.removed_rows]
                if available_rows:
                    row_to_remove = random.choice(available_rows)
                    self.removed_rows.add(row_to_remove)
                    
                    # O satırdaki tüm kutuları gizle
                    for col in range(self.grid_size):
                        self.boxes[row_to_remove][col].hide()
                    
                    # Kutuları ortaya doğru topla
                    self.collapse_rows()
            
            # Tüm satırlar silindiyse animasyonu durdur
            if len(self.removed_rows) >= self.grid_size - 1:
                self.color_animation_timer.stop()
                QTimer.singleShot(500, self.animate_boxes_fade_out)
        
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(random_box_animation)
        self.color_animation_timer.start(30)  # Her 30ms'de bir güncelle - daha hızlı
    
    def collapse_rows(self):
        """Silinen satırları yukarıya doğru topla - status bar yukarı çıkıyor"""
        # Görünür satırları bul
        visible_rows = []
        for row in range(self.grid_size):
            if row not in self.removed_rows:
                visible_rows.append(row)
        
        if not visible_rows:
            return
            
        # Üstten başlayarak yerleştir - yukarı doğru itiliyormuş gibi
        start_row = 0
        
        # Önce tüm kutuları gizle
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.boxes[row][col].hide()
        
        # Görünür kutuları üstten başlayarak yerleştir
        for i, visible_row in enumerate(visible_rows):
            target_row = start_row + i
            if 0 <= target_row < self.grid_size:
                for col in range(self.grid_size):
                    # Saklanan style'ı kullan
                    if visible_row < len(self.box_states) and col < len(self.box_states[visible_row]):
                        style = self.box_states[visible_row][col]
                        if style:
                            self.boxes[target_row][col].setStyleSheet(style)
                        else:
                            # Varsayılan koyu stil
                            self.boxes[target_row][col].setStyleSheet("""
                                background-color: rgba(20, 20, 20, 100);
                                border-radius: 0px;
                            """)
                    self.boxes[target_row][col].show()
        
        # Status bar sabit kalsın - hareket etmesin
        pass
        
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