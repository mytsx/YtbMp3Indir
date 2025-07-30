from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QLabel, 
                            QGraphicsOpacityEffect, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtGui import QFont
import random
import math
import time
import traceback
import sys


class SplashScreen(QWidget):
    """Matematiksel desenlerle özel splash screen"""
    
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
        self.grid_layout.setSpacing(5)
        
        # Kutular için liste
        self.boxes = []
        self.box_animations = []
        
        # 16x16 grid - daha yüksek çözünürlük
        self.grid_size = 16
        box_size = 25
        
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
                animation.setDuration(50)  # Çok hızlı fade in
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
        
        # Random seed ve renk paleti
        self.pattern_seed = time.time()
        self.time_step = 0
        self.color_palette = self.generate_random_palette()
        
        
    def generate_random_palette(self):
        """Her desen için rastgele renk paleti oluştur"""
        # Tamamen rastgele RGB değerleri
        return {
            'primary': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
            'secondary': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
            'accent': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
            'background': (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))
        }
        
    def get_random_color(self):
        """Tamamen rastgele bir renk döndür"""
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        
        # Kutuları animasyonla göster
        self.animate_boxes_fade_in()
        
        # Matematiksel desen animasyonu
        QTimer.singleShot(800, self.start_mathematical_pattern)
        
        # Fade out kaldırıldı - direkt finished sinyali gönder
        # QTimer.singleShot(2500, self.animate_boxes_fade_out)
    
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
        self.animation_timer.start(3)  # Her 3ms'de bir kutu - çok hızlı
        
    def start_mathematical_pattern(self):
        """Matematiksel desen animasyonu"""
        # Desen seçimi (her açılışta farklı)
        pattern_type = int(self.pattern_seed) % 6
        
        patterns = {
            0: self.prime_spiral_pattern,      # Asal sayı spirali
            1: self.golden_spiral_pattern,     # Altın spiral
            2: self.fractal_tree_pattern,      # Fraktal ağaç
            3: self.euler_curve_pattern,       # Euler eğrisi
            4: self.fibonacci_flower_pattern,  # Fibonacci çiçeği
            5: self.koch_snowflake_pattern     # Koch kar tanesi fraktalı
        }
        
        self.active_pattern = patterns[pattern_type]
        self.pattern_name = ["Asal Spiral", "Altın Spiral", "Fraktal Ağaç", 
                           "Euler Eğrisi", "Fibonacci Çiçeği", "Koch Kar Tanesi"][pattern_type]
        
        # Her desen için yeni renk paleti
        self.color_palette = self.generate_random_palette()
        
        # Desen adını göster
        self.update_status(f"Matematiksel Desen: {self.pattern_name}")
        
        def safe_pattern_update():
            try:
                print(f"[SPLASH] Running pattern: {self.pattern_name}, Time step: {self.time_step}")
                self.active_pattern()
            except Exception as e:
                print(f"[SPLASH ERROR] Pattern '{self.pattern_name}' failed at time_step {self.time_step}")
                print(f"[SPLASH ERROR] Exception type: {type(e).__name__}")
                print(f"[SPLASH ERROR] Exception message: {str(e)}")
                print(f"[SPLASH ERROR] Full traceback:")
                traceback.print_exc()
                
                # Hata durumunda basit bir animasyon göster
                try:
                    for row in range(self.grid_size):
                        for col in range(self.grid_size):
                            hue = (row * col + self.time_step) % 360
                            r = int(127 + 127 * math.sin(hue * math.pi / 180))
                            g = int(127 + 127 * math.sin((hue + 120) * math.pi / 180))
                            b = int(127 + 127 * math.sin((hue + 240) * math.pi / 180))
                            self.boxes[row][col].setStyleSheet(f"""
                                background-color: rgba({r}, {g}, {b}, 200);
                                border-radius: 0px;
                            """)
                except Exception as fallback_error:
                    print(f"[SPLASH CRITICAL] Even fallback animation failed: {fallback_error}")
                    traceback.print_exc()
                
                self.time_step += 1
        
        self.color_animation_timer = QTimer()
        self.color_animation_timer.timeout.connect(safe_pattern_update)
        self.color_animation_timer.start(20)  # Her 20ms'de güncelle - çok hızlı
        
    def prime_spiral_pattern(self):
        """Ulam spirali - Asal sayıların spiral deseni"""
        try:
            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(math.sqrt(n)) + 1):
                    if n % i == 0:
                        return False
                return True
            
            center = self.grid_size // 2
            
            # Tamamen rastgele arka plan rengi
            bg_r = random.randint(10, 50)
            bg_g = random.randint(10, 50)
            bg_b = random.randint(10, 50)
            
            # Önce tüm kutuları koyu arka plan yap
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.boxes[row][col].setStyleSheet(f"""
                        background-color: rgba({bg_r}, {bg_g}, {bg_b}, 200);
                        border-radius: 0px;
                    """)
            
            # Ulam spirali oluştur - düzgün spiral algoritması
            x, y = center, center
            dx, dy = 1, 0  # Sağa başla
            num = 1
            steps = 1
            step_count = 0
            direction_changes = 0
            
            # Spiral boyunca ilerle
            for i in range(min(self.grid_size * self.grid_size, 500)):  # Maksimum 500 sayı kontrol et
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    if is_prime(num):
                        # Tamamen rastgele parlak renkler
                        r = random.randint(150, 255)
                        g = random.randint(150, 255)
                        b = random.randint(150, 255)
                        
                        # Animasyon efekti
                        phase = (num * 0.1 + self.time_step * 0.05) % (2 * math.pi)
                        brightness = 0.7 + 0.3 * math.sin(phase)
                        
                        r = min(255, int(r * brightness))
                        g = min(255, int(g * brightness))
                        b = min(255, int(b * brightness))
                        
                        self.boxes[y][x].setStyleSheet(f"""
                            background-color: rgba({r}, {g}, {b}, 240);
                            border-radius: 0px;
                        """)
                
                # Bir adım ilerle
                x += dx
                y += dy
                step_count += 1
                
                # Yön değiştirme kontrolü
                if step_count == steps:
                    step_count = 0
                    direction_changes += 1
                    
                    # 90 derece saat yönünde dön
                    dx, dy = -dy, dx
                    
                    # Her iki yön değişiminde adım sayısını artır
                    if direction_changes % 2 == 0:
                        steps += 1
                
                num += 1
                
                # Grid dışına çıktıysak dur
                if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
                    # Merkeze yakın bir noktada devam etmeyi dene
                    if abs(x - center) > self.grid_size // 2 + 2 or abs(y - center) > self.grid_size // 2 + 2:
                        break
            
            self.time_step += 1
        except Exception as e:
            print(f"[SPIRAL ERROR] Prime spiral failed: {e}")
            traceback.print_exc()
            self.time_step += 1
        
    def golden_spiral_pattern(self):
        """Altın spiral - Fibonacci ve altın oran"""
        center_x = self.grid_size / 2
        center_y = self.grid_size / 2
        golden_ratio = 1.618033988749895
        
        # Rastgele arka plan rengi
        bg_r, bg_g, bg_b = self.color_palette['background']
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.boxes[row][col].setStyleSheet(f"""
                    background-color: rgba({bg_r}, {bg_g}, {bg_b}, 180);
                    border-radius: 0px;
                """)
        
        # Altın spiral çiz
        # b = ln(φ) / (π/2)
        b = math.log(golden_ratio) / (math.pi / 2)
        
        # Spiral üzerinde birçok nokta çiz
        for i in range(500):  # Daha fazla nokta
            theta = i * 0.1  # Açı artışı
            
            # Altın spiral denklemi: r = a * e^(b*theta)
            r = 0.5 * math.exp(b * theta)
            
            # Kartezyen koordinatlara çevir
            x = center_x + r * math.cos(theta + self.time_step * 0.02)
            y = center_y + r * math.sin(theta + self.time_step * 0.02)
            
            # Grid koordinatları
            grid_x = int(x)
            grid_y = int(y)
            
            # Grid içinde mi kontrol et
            if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                # Spiral üzerindeki noktayı parlat
                hue = (theta * 180 / math.pi + self.time_step * 2) % 360
                
                # HSV'den RGB'ye
                c = 1.0
                x_hsv = c * (1 - abs((hue / 60) % 2 - 1))
                m = 0
                
                if hue < 60:
                    r_norm, g_norm, b_norm = c, x_hsv, 0
                elif hue < 120:
                    r_norm, g_norm, b_norm = x_hsv, c, 0
                elif hue < 180:
                    r_norm, g_norm, b_norm = 0, c, x_hsv
                elif hue < 240:
                    r_norm, g_norm, b_norm = 0, x_hsv, c
                elif hue < 300:
                    r_norm, g_norm, b_norm = x_hsv, 0, c
                else:
                    r_norm, g_norm, b_norm = c, 0, x_hsv
                
                # Parlaklık
                brightness = 200 + int(55 * math.sin(i * 0.1 + self.time_step * 0.05))
                r_color = int(brightness * r_norm)
                g_color = int(brightness * g_norm)
                b_color = int(brightness * b_norm)
                
                self.boxes[grid_y][grid_x].setStyleSheet(f"""
                    background-color: rgba({r_color}, {g_color}, {b_color}, 250);
                    border-radius: 0px;
                """)
                
                # Çevresindeki kutulara da yumuşak geçiş ekle
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = grid_y + dy, grid_x + dx
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and (dx != 0 or dy != 0):
                            current_style = self.boxes[ny][nx].styleSheet()
                            if 'rgba(10, 15, 25' in current_style:  # Sadece arka plan kutularını güncelle
                                fade = 0.3
                                self.boxes[ny][nx].setStyleSheet(f"""
                                    background-color: rgba({int(r_color*fade)}, {int(g_color*fade)}, {int(b_color*fade)}, 150);
                                    border-radius: 0px;
                                """)
            
            # Spiral dışına çıktıysa dur
            if r > self.grid_size * 0.7:
                break
        
        self.time_step += 1
        
    def fractal_tree_pattern(self):
        """Fraktal ağaç deseni - L-sistem"""
        center_x = self.grid_size // 2
        bottom_y = self.grid_size - 1
        
        # Gece gökyüzü arka planı
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Üst kısımlar daha koyu (gece gökyüzü)
                darkness = 10 + int(row * 20 / self.grid_size)
                self.boxes[row][col].setStyleSheet(f"""
                    background-color: rgba({darkness}, {darkness}, {darkness + 10}, 180);
                    border-radius: 0px;
                """)
        
        # Fraktal ağaç parametreleri
        branches_drawn = []  # Çizilen dalları sakla
        
        def draw_branch(x, y, angle, length, depth, thickness=3):
            if depth <= 0 or length < 1:
                return
                
            # Dal sonu pozisyonu
            end_x = x + length * math.cos(angle)
            end_y = y - length * math.sin(angle)
            
            # Dalı çiz (Bresenham benzeri)
            steps = int(length * 2)
            for i in range(steps):
                t = i / float(steps)
                curr_x = x + t * (end_x - x)
                curr_y = y + t * (end_y - y)
                
                # Kalınlık için çevresindeki kutuları da boya
                for dx in range(-thickness//2, thickness//2 + 1):
                    for dy in range(-thickness//2, thickness//2 + 1):
                        grid_x = int(curr_x + dx)
                        grid_y = int(curr_y + dy)
                        
                        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                            # Derinliğe göre rastgele renkler
                            if depth > 3:  # Gövde
                                base_r, base_g, base_b = self.color_palette['primary']
                            elif depth > 1:  # Dallar
                                base_r, base_g, base_b = self.color_palette['secondary']
                            else:  # Yapraklar
                                base_r, base_g, base_b = self.color_palette['accent']
                            
                            # Animasyon için parlaklık
                            phase = self.time_step * 0.05 + x * 0.1 + y * 0.1
                            brightness = 0.7 + 0.3 * math.sin(phase)
                            
                            r = int(base_r * brightness)
                            g = int(base_g * brightness)
                            b = int(base_b * brightness)
                            
                            opacity = 200 + int(55 * math.sin(depth * 0.5))
                            self.boxes[grid_y][grid_x].setStyleSheet(f"""
                                background-color: rgba({r}, {g}, {b}, {opacity});
                                border-radius: 0px;
                            """)
            
            # Dallanma
            if depth > 0:
                # Doğal dallanma açıları
                angle_base = math.pi / 5  # 36 derece
                angle_variation = math.sin(self.time_step * 0.02 + depth) * 0.2
                
                # Dal uzunluk oranı (altın oran yakını)
                length_ratio = 0.618 + math.sin(self.time_step * 0.01) * 0.05
                
                # Çoklu dallanma (depth'e göre)
                if depth > 2:
                    # 2 ana dal
                    draw_branch(end_x, end_y, angle - angle_base - angle_variation, 
                               length * length_ratio, depth - 1, max(1, thickness - 1))
                    draw_branch(end_x, end_y, angle + angle_base + angle_variation, 
                               length * length_ratio, depth - 1, max(1, thickness - 1))
                else:
                    # Uç kısımlarda daha fazla dal
                    for i in range(3):
                        branch_angle = angle + (i - 1) * angle_base * 0.7
                        draw_branch(end_x, end_y, branch_angle + angle_variation, 
                                   length * length_ratio * 0.8, depth - 1, 1)
        
        # Ana gövdeyi başlat
        initial_length = self.grid_size * 0.35  # Ekrana göre ölçekle
        draw_branch(center_x, bottom_y, math.pi / 2, initial_length, 6, 4)
        
        self.time_step += 1
        
    def euler_curve_pattern(self):
        """Euler eğrisi - e^(i*theta) karmaşık sayı deseni"""
        center_x = self.grid_size / 2
        center_y = self.grid_size / 2
        scale = 4.0 / self.grid_size  # Grid boyutuna göre ölçekle
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Karmaşık düzlem koordinatları (-2 ile 2 arasında)
                z_real = (col - center_x) * scale
                z_imag = (row - center_y) * scale
                
                # Animasyonlu karmaşık fonksiyon
                # f(z) = e^(i*z*t) burada t = time_step
                t = self.time_step * 0.02
                
                # z * t hesapla
                zt_real = z_real * math.cos(t) - z_imag * math.sin(t)
                zt_imag = z_real * math.sin(t) + z_imag * math.cos(t)
                
                # e^(i*z*t) hesapla
                # e^(i*(a+bi)) = e^(-b) * e^(i*a)
                magnitude = math.exp(-zt_imag)
                phase = zt_real
                
                # Euler formülü: e^(i*θ) = cos(θ) + i*sin(θ)
                real_part = magnitude * math.cos(phase)
                imag_part = magnitude * math.sin(phase)
                
                # Görsel efektler için ek hesaplamalar
                # Modulus (büyüklük)
                modulus = math.sqrt(real_part**2 + imag_part**2)
                # Argüman (açı)
                argument = math.atan2(imag_part, real_part)
                
                # Renklendirme - karmaşık faz görünümü
                hue = (argument * 180 / math.pi + 180) % 360
                
                # Parlaklık - modüle göre, periyodik yapıda
                # Log ölçekleme daha iyi görsel sonuç verir
                if modulus > 0:
                    log_modulus = math.log(modulus + 1)
                    brightness = int(127 + 127 * math.sin(log_modulus * 5))
                else:
                    brightness = 0
                
                # Rastgele renk paleti kullan
                # Modulus'a göre farklı renkler
                color_index = int(modulus * 10) % 3
                if color_index == 0:
                    base_r, base_g, base_b = self.color_palette['primary']
                elif color_index == 1:
                    base_r, base_g, base_b = self.color_palette['secondary']
                else:
                    base_r, base_g, base_b = self.color_palette['accent']
                
                # Parlaklık faktörü
                brightness_factor = brightness / 255.0
                r = base_r * brightness_factor
                g = base_g * brightness_factor
                b = base_b * brightness_factor
                
                # Kontur çizgileri için ek efekt
                contour = int(modulus * 10) % 2
                if contour == 0:
                    r, g, b = int(r * 0.7), int(g * 0.7), int(b * 0.7)
                
                opacity = 200 + int(55 * math.sin(modulus + self.time_step * 0.1))
                
                self.boxes[row][col].setStyleSheet(f"""
                    background-color: rgba({int(r)}, {int(g)}, {int(b)}, {opacity});
                    border-radius: 0px;
                """)
        
        self.time_step += 1
        
    def fibonacci_flower_pattern(self):
        """Fibonacci çiçeği - Doğadaki spiral düzen"""
        center_x = self.grid_size / 2
        center_y = self.grid_size / 2
        golden_angle = 137.5077640500378  # Altın açı (derece)
        
        # Koyu mavi-mor arka plan (gece bahçesi)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Merkeze yaklaştıkça hafif aydınlık
                dx = col - center_x
                dy = row - center_y
                dist = math.sqrt(dx*dx + dy*dy) / (self.grid_size * 0.7)
                dist = max(0, min(1, dist))  # 0-1 arasında sınırla
                darkness = max(10, min(25, 10 + int(15 * (1 - dist))))
                self.boxes[row][col].setStyleSheet(f"""
                    background-color: rgba({darkness}, {darkness + 5}, {darkness + 15}, 200);
                    border-radius: 0px;
                """)
        
        # Daha fazla nokta için grid boyutuna göre ölçekle
        num_points = min(200, self.grid_size * self.grid_size // 4)  # Maksimum 200 nokta
        scale = self.grid_size / 16.0  # 16x16 grid için normalize
        
        # Her nokta bir tohum/çiçek yaprağı temsil eder
        for i in range(num_points):
            # Fibonacci spiral düzeni
            angle = i * golden_angle * math.pi / 180
            # Doğrusal olmayan büyüme - doğadaki gibi
            radius = scale * math.sqrt(i) * 0.8
            
            # Animasyonlu dönüş
            rotation = self.time_step * 0.01
            x = center_x + radius * math.cos(angle + rotation)
            y = center_y + radius * math.sin(angle + rotation)
            
            # Grid sınırları kontrolü
            if radius > self.grid_size * 0.45:  # Dış sınır
                continue
                
            # Çiçek yaprakları için koordinatlar
            grid_x = int(x)
            grid_y = int(y)
            
            if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                # Çiçek merkezi için rastgele renkler
                # Her bölge için farklı renk
                if i < num_points * 0.2:  # Merkez
                    base_r, base_g, base_b = self.color_palette['primary']
                elif i < num_points * 0.5:  # Orta
                    base_r, base_g, base_b = self.color_palette['secondary']
                else:  # Dış yapraklar
                    base_r, base_g, base_b = self.color_palette['accent']
                
                # Animasyon için parlaklık değişimi
                pulse = math.sin(i * 0.1 + self.time_step * 0.05)
                brightness_factor = 0.7 + 0.3 * pulse
                
                r = min(255, max(0, int(base_r * brightness_factor)))
                g = min(255, max(0, int(base_g * brightness_factor)))
                b = min(255, max(0, int(base_b * brightness_factor)))
                
                # Spiral desenini vurgula
                spiral_highlight = math.sin(angle * 13)  # 13 spiral kolu
                if spiral_highlight > 0.5:
                    r = min(255, int(r * 1.2))
                    g = min(255, int(g * 1.2))
                    b = min(255, int(b * 1.1))
                
                opacity = min(255, max(0, 220 + int(35 * pulse)))
                
                # Ana nokta
                self.boxes[grid_y][grid_x].setStyleSheet(f"""
                    background-color: rgba({r}, {g}, {b}, {opacity});
                    border-radius: 0px;
                """)
                
                # Çiçek yaprağı efekti için çevre
                if i > num_points * 0.3:  # Sadece dış kısımlar için
                    petal_size = 1 if i < num_points * 0.6 else 2
                    petal_size = min(2, max(1, petal_size))  # Güvenlik için sınırla
                    for dy in range(-petal_size, petal_size + 1):
                        for dx in range(-petal_size, petal_size + 1):
                            if dx == 0 and dy == 0:
                                continue
                            ny, nx = grid_y + dy, grid_x + dx
                            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                                # Mesafeye göre fade
                                dist = math.sqrt(dx*dx + dy*dy)
                                fade = math.exp(-dist * 0.8)
                                fr = min(255, max(0, int(r*fade*0.6)))
                                fg = min(255, max(0, int(g*fade*0.6)))
                                fb = min(255, max(0, int(b*fade*0.5)))
                                fo = min(255, max(0, int(opacity*fade*0.7)))
                                self.boxes[ny][nx].setStyleSheet(f"""
                                    background-color: rgba({fr}, {fg}, {fb}, {fo});
                                    border-radius: 0px;
                                """)
        
        self.time_step += 1
        
    def koch_snowflake_pattern(self):
        """Koch kar tanesi fraktalı - Matematiksel kar tanesi"""
        try:
            center_x = int(self.grid_size / 2)
            center_y = int(self.grid_size / 2)
            
            # Koyu mavi kar gecesi arka planı
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.boxes[row][col].setStyleSheet("""
                        background-color: rgba(5, 10, 25, 240);
                        border-radius: 0px;
                    """)
            
            # Kar tanesi çizim fonksiyonu - Bresenham algoritması
            def draw_line(x0, y0, x1, y1, color=(255, 255, 255)):
                """İki nokta arasında çizgi çiz"""
                points = []
                dx = abs(x1 - x0)
                dy = abs(y1 - y0)
                sx = 1 if x0 < x1 else -1
                sy = 1 if y0 < y1 else -1
                err = dx - dy
                
                while True:
                    points.append((x0, y0))
                    
                    if x0 == x1 and y0 == y1:
                        break
                        
                    e2 = 2 * err
                    if e2 > -dy:
                        err -= dy
                        x0 += sx
                    if e2 < dx:
                        err += dx
                        y0 += sy
                
                return points
            
            # 6 kollu kar tanesi çiz
            rotation = self.time_step * 0.01
            
            # Ana kollar (6 adet)
            main_length = int(self.grid_size * 0.4)
            for i in range(6):
                angle = (math.pi * 2 * i / 6) + rotation
                
                # Ana kol
                end_x = int(center_x + main_length * math.cos(angle))
                end_y = int(center_y + main_length * math.sin(angle))
                
                # Ana kolu çiz
                main_points = draw_line(center_x, center_y, end_x, end_y)
                
                # Ana kol üzerindeki noktaları beyazla
                for x, y in main_points:
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        # Parlak beyaz
                        self.boxes[y][x].setStyleSheet("""
                            background-color: rgba(255, 255, 255, 255);
                            border-radius: 0px;
                        """)
                
                # Yan dallar ekle
                for j in range(2, 5):  # 3 yan dal
                    branch_start = j * len(main_points) // 6
                    if branch_start < len(main_points):
                        branch_x, branch_y = main_points[branch_start]
                        branch_length = main_length // (j + 1)
                        
                        # Sol dal
                        left_angle = angle - math.pi / 4  # 45 derece sol
                        left_end_x = int(branch_x + branch_length * math.cos(left_angle))
                        left_end_y = int(branch_y + branch_length * math.sin(left_angle))
                        
                        left_points = draw_line(branch_x, branch_y, left_end_x, left_end_y)
                        for x, y in left_points:
                            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                                self.boxes[y][x].setStyleSheet("""
                                    background-color: rgba(240, 245, 255, 250);
                                    border-radius: 0px;
                                """)
                        
                        # Sağ dal
                        right_angle = angle + math.pi / 4  # 45 derece sağ
                        right_end_x = int(branch_x + branch_length * math.cos(right_angle))
                        right_end_y = int(branch_y + branch_length * math.sin(right_angle))
                        
                        right_points = draw_line(branch_x, branch_y, right_end_x, right_end_y)
                        for x, y in right_points:
                            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                                self.boxes[y][x].setStyleSheet("""
                                    background-color: rgba(240, 245, 255, 250);
                                    border-radius: 0px;
                                """)
            
            # Merkeze parlak nokta
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    cx, cy = center_x + dx, center_y + dy
                    if 0 <= cx < self.grid_size and 0 <= cy < self.grid_size:
                        self.boxes[cy][cx].setStyleSheet("""
                            background-color: rgba(255, 255, 255, 255);
                            border-radius: 0px;
                        """)
            
            self.time_step += 1
            
        except Exception as e:
            print(f"Koch snowflake error: {e}")
            traceback.print_exc()
            self.time_step += 1
        
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