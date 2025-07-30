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
            
            # Önce tüm kutuları koyu yap
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.boxes[row][col].setStyleSheet("""
                        background-color: rgba(20, 20, 20, 150);
                        border-radius: 0px;
                    """)
            
            # Ulam spirali oluştur
            x, y = center, center
            dx, dy = 0, -1  # Yukarı başla
            num = 1
            
            for _ in range(self.grid_size * self.grid_size):
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    if is_prime(num):
                        # Asal sayılar için animasyonlu renk
                        phase = (num * 0.1 + self.time_step * 0.05) % (2 * math.pi)
                        brightness = 0.7 + 0.3 * math.sin(phase)
                        
                        # Renk paletinden renk al
                        if num < 100:
                            r, g, b = self.color_palette['primary']
                        elif num < 300:
                            r, g, b = self.color_palette['secondary']
                        else:
                            r, g, b = self.color_palette['accent']
                        
                        # Parlaklık uygula
                        r = min(255, int(r * brightness))
                        g = min(255, int(g * brightness))
                        b = min(255, int(b * brightness))
                        
                        self.boxes[y][x].setStyleSheet(f"""
                            background-color: rgba({r}, {g}, {b}, 220);
                            border-radius: 0px;
                        """)
                
                # Spiral hareketi
                if x == center + dx and y == center + dy:
                    dx, dy = -dy, dx  # 90 derece dön
                x += dx
                y += dy
                num += 1
                
                if abs(x - center) > self.grid_size // 2 and abs(y - center) > self.grid_size // 2:
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
            center_x = self.grid_size / 2
            center_y = self.grid_size / 2
            
            # Koyu mavi kar gecesi arka planı
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.boxes[row][col].setStyleSheet("""
                        background-color: rgba(10, 20, 40, 220);
                        border-radius: 0px;
                    """)
            
            # Kar tanesi noktalarını sakla
            snowflake_points = []
            
            # Koch kar tanesi algoritması - sadece noktaları hesapla
            def calculate_koch_points(x1, y1, x2, y2, depth):
                if depth == 0:
                    # Çizgi üzerindeki noktaları ekle
                    steps = int(math.sqrt((x2-x1)**2 + (y2-y1)**2))
                    for i in range(steps):
                        t = i / float(max(1, steps))
                        x = x1 + t * (x2 - x1)
                        y = y1 + t * (y2 - y1)
                        snowflake_points.append((int(x), int(y)))
                else:
                    # Koch algoritması
                    dx = x2 - x1
                    dy = y2 - y1
                    
                    # 4 nokta hesapla
                    x_a = x1 + dx / 3
                    y_a = y1 + dy / 3
                    
                    x_b = x1 + 2 * dx / 3
                    y_b = y1 + 2 * dy / 3
                    
                    # Üçgenin tepe noktası
                    angle = -math.pi / 3
                    dx_small = (x_b - x_a)
                    dy_small = (y_b - y_a)
                    
                    x_c = x_a + dx_small * math.cos(angle) - dy_small * math.sin(angle)
                    y_c = y_a + dx_small * math.sin(angle) + dy_small * math.cos(angle)
                    
                    # Recursive çağrılar
                    calculate_koch_points(x1, y1, x_a, y_a, depth - 1)
                    calculate_koch_points(x_a, y_a, x_c, y_c, depth - 1)
                    calculate_koch_points(x_c, y_c, x_b, y_b, depth - 1)
                    calculate_koch_points(x_b, y_b, x2, y2, depth - 1)
            
            # 6 köşeli kar tanesi
            radius = self.grid_size * 0.35
            rotation = self.time_step * 0.01
            depth = 2  # Daha az derinlik
            
            # 6 köşe noktası
            vertices = []
            for i in range(6):
                angle = (2 * math.pi * i / 6) + rotation
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                vertices.append((x, y))
            
            # Her kenar için Koch eğrisi hesapla
            for i in range(6):
                next_i = (i + 1) % 6
                calculate_koch_points(vertices[i][0], vertices[i][1],
                                    vertices[next_i][0], vertices[next_i][1], depth)
            
            # Hesaplanan noktaları kutulara dönüştür
            drawn = set()
            for x, y in snowflake_points:
                # 3x3 alan boyası (kalınlık için)
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        grid_x = x + dx
                        grid_y = y + dy
                        
                        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                            if (grid_x, grid_y) not in drawn:
                                drawn.add((grid_x, grid_y))
                                
                                # Beyaz kar tanesi
                                # Hafif mavimsi beyaz tonları
                                pulse = math.sin(self.time_step * 0.05 + grid_x * 0.1 + grid_y * 0.1)
                                brightness = 0.85 + 0.15 * pulse
                                
                                # Beyaz tonları (hafif mavi tonu ile)
                                r = min(255, int(240 * brightness))
                                g = min(255, int(245 * brightness))
                                b = min(255, int(255 * brightness))
                                
                                self.boxes[grid_y][grid_x].setStyleSheet(f"""
                                    background-color: rgba({r}, {g}, {b}, 250);
                                    border-radius: 0px;
                                """)
            
            self.time_step += 1
            
        except Exception as e:
            print(f"Koch snowflake error: {e}")
            # Hata durumunda basit kar tanesi
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if (row + col) % 2 == 0:
                        self.boxes[row][col].setStyleSheet("""
                            background-color: rgba(200, 200, 255, 200);
                            border-radius: 0px;
                        """)
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