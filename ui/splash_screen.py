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
                    background-color: rgba(0, 0, 0, 0);
                    border: none;
                """)
                
                self.grid_layout.addWidget(box, row, col)
                box_row.append(box)
                
                # Opacity efekti
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0)  # Başlangıçta GÖRÜNMEZ
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
        self.app_ready = False  # Uygulama hazır mı?
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        
        # Fade in animasyonu YAPMA - direkt rastgele animasyona geç
        # self.animate_boxes_fade_in()  # BUNU YAPMA
        
        # Rastgele kutu animasyonu HEMEN başlat
        QTimer.singleShot(100, self.start_random_animation)
    
    def update_status(self, message):
        """Durum mesajını güncelle"""
        self.status_label.setText(message)
    
    def set_app_ready(self):
        """Uygulama hazır olduğunda çağrılır"""
        self.app_ready = True
        # Animasyonu durdur ve pencereyi kapat
        if hasattr(self, 'color_animation_timer') and self.color_animation_timer:
            self.color_animation_timer.stop()
        
        # Son bir kez tüm kutuları renklendir
        color_palettes = [
            [(255, 0, 128), (0, 255, 255), (255, 255, 0), (128, 255, 0), (255, 0, 255)],
            [(255, 182, 193), (176, 224, 230), (255, 218, 185), (221, 160, 221), (152, 251, 152)],
            [(255, 69, 0), (50, 205, 50), (30, 144, 255), (255, 215, 0), (138, 43, 226)],
            [(70, 130, 180), (64, 224, 208), (72, 209, 204), (95, 158, 160), (176, 196, 222)],
            [(255, 99, 71), (255, 140, 0), (255, 165, 0), (255, 192, 203), (219, 112, 147)]
        ]
        palette = random.choice(color_palettes)
        
        self.color_all_boxes(palette)
        # KUTULARI SİLMEDEN direkt kapat
        QTimer.singleShot(200, self.close_splash)
        
    def animate_boxes_fade_in(self):
        """Kutuları sırayla fade in yap - sadece görünür olanlar için"""
        def show_next_box():
            if self.current_animation_index < len(self.box_animations):
                # Sadece görünür kutular için animasyon yap
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
        """Ortadan dışarı doğru açılan animasyon"""
        self.update_status("Yükleniyor...")
        
        # Ortadan başla
        center = self.grid_size // 2
        
        # Hangi satırların görünür olduğunu takip et
        self.visible_rows = set()
        self.animation_count = 0
        # Her kutunun durumunu sakla
        self.box_states = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Başlangıçta tüm kutuları TRANSPARAN yap
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Tamamen şeffaf başlat
                style = """
                    background-color: rgba(0, 0, 0, 0);
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
        
        # İlk görünür satırları ortada başlat ve göster
        self.visible_rows.add(center)
        self.visible_rows.add(center - 1)
        
        # Ortadaki satırları koyu renkle göster ve GÖRÜNÜR yap
        for row in [center - 1, center]:
            for col in range(self.grid_size):
                style = """
                    background-color: rgba(20, 20, 20, 100);
                    border-radius: 0px;
                """
                self.boxes[row][col].setStyleSheet(style)
                self.box_states[row][col] = style
                # Opacity'yi 1 yap - GÖRÜNÜR
                opacity = self.boxes[row][col].graphicsEffect()
                if opacity:
                    opacity.setOpacity(1)
        
        def random_box_animation():
            nonlocal current_palette
            
            # TÜM kutular zaten görünür - show() yapmaya gerek yok
            
            # Her frame'de rastgele birkaç kutu renklendir - genişleme aşamasında
            if len(self.visible_rows) < self.grid_size:
                # Sadece "görünür" kabul edilen satırlarda renk değiştir (animasyon efekti için)
                for _ in range(10):  # Her seferinde 10 kutu - daha hızlı renklendirme
                    if self.visible_rows:
                        row = random.choice(list(self.visible_rows))
                        col = random.randint(0, self.grid_size - 1)
                        
                        # TAMAMEN RASTGELE RENKLER - palet kullanma
                        r = random.randint(50, 255)
                        g = random.randint(50, 255)
                        b = random.randint(50, 255)
                        
                        style = f"""
                            background-color: rgba({r}, {g}, {b}, 200);
                            border-radius: 0px;
                        """
                        self.boxes[row][col].setStyleSheet(style)
                        self.box_states[row][col] = style
                
                # Kutuları söndürme - hepsi renkli kalsın
            
            # Palet kullanmıyoruz artık - tamamen rastgele
            
            # Her 3 frame'de yeni satır ekle - hızlı ama görünür
            self.animation_count += 1
            if self.animation_count % 3 == 0 and len(self.visible_rows) < self.grid_size:
                # Yukarı ve aşağı genişlet
                min_visible = min(self.visible_rows)
                max_visible = max(self.visible_rows)
                
                # Üste doğru genişle
                if min_visible > 0:
                    new_row = min_visible - 1
                    self.visible_rows.add(new_row)
                    # Yeni satırdaki kutuları koyu renkle göster ve GÖRÜNÜR yap
                    for col in range(self.grid_size):
                        style = """
                            background-color: rgba(20, 20, 20, 100);
                            border-radius: 0px;
                        """
                        self.boxes[new_row][col].setStyleSheet(style)
                        self.box_states[new_row][col] = style
                        # Opacity'yi 1 yap - GÖRÜNÜR
                        opacity = self.boxes[new_row][col].graphicsEffect()
                        if opacity:
                            opacity.setOpacity(1)
                
                # Alta doğru genişle
                if max_visible < self.grid_size - 1:
                    new_row = max_visible + 1
                    self.visible_rows.add(new_row)
                    # Yeni satırdaki kutuları koyu renkle göster ve GÖRÜNÜR yap
                    for col in range(self.grid_size):
                        style = """
                            background-color: rgba(20, 20, 20, 100);
                            border-radius: 0px;
                        """
                        self.boxes[new_row][col].setStyleSheet(style)
                        self.box_states[new_row][col] = style
                        # Opacity'yi 1 yap - GÖRÜNÜR
                        opacity = self.boxes[new_row][col].graphicsEffect()
                        if opacity:
                            opacity.setOpacity(1)
            
            # Tüm satırlar görünür olduysa
            if len(self.visible_rows) >= self.grid_size:
                # Logaritmik hızla doldur
                if not hasattr(self, 'fill_phase'):
                    self.fill_phase = True
                    self.fill_speed = 2  # Başlangıç hızı
                
                # Logaritmik artan hızla kutular renklendir
                if self.fill_phase:
                    # Hızı logaritmik artır (maksimuma ulaşana kadar)
                    if self.fill_speed < 50:
                        self.fill_speed = int(self.fill_speed * 1.15)  # %15 artış
                    
                    for _ in range(min(self.fill_speed, 50)):  # Max 50 kutu per frame
                        row = random.randint(0, self.grid_size - 1)
                        col = random.randint(0, self.grid_size - 1)
                        
                        # TAMAMEN RASTGELE RENKLER
                        r = random.randint(50, 255)
                        g = random.randint(50, 255)
                        b = random.randint(50, 255)
                        
                        style = f"""
                            background-color: rgba({r}, {g}, {b}, 200);
                            border-radius: 0px;
                        """
                        self.boxes[row][col].setStyleSheet(style)
                
                # Uygulama hazır değilse renkleri değiştirmeye devam et
                # Hiçbir zaman otomatik fade out yapma!
        
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(random_box_animation)
        self.color_animation_timer.start(40)  # Her 40ms'de bir güncelle - daha yavaş
    
    def color_all_boxes(self, palette):
        """Tüm kutuları renklendir - koyu olanları da"""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # TAMAMEN RASTGELE RENKLER
                r = random.randint(50, 255)
                g = random.randint(50, 255)
                b = random.randint(50, 255)
                
                style = f"""
                    background-color: rgba({r}, {g}, {b}, 200);
                    border-radius: 0px;
                """
                self.boxes[row][col].setStyleSheet(style)
    
    def animate_boxes_fade_out(self):
        """Animasyonu durdur ve pencereyi kapat - KUTULARI SİLME!"""
        if self.color_animation_timer:
            self.color_animation_timer.stop()
        
        # KUTULARI FADE OUT YAPMA! Direkt pencereyi kapat
        QTimer.singleShot(100, self.close_splash)
        
    def close_splash(self):
        """Splash screen'i kapat"""
        self.close()
        self.finished.emit()