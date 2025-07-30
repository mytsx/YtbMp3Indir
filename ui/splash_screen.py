from PyQt5.QtWidgets import QSplashScreen, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QFont, QLinearGradient


class SplashScreen(QSplashScreen):
    """Şaşalı açılış ekranı"""
    
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Splash screen boyutu
        splash_width = 600
        splash_height = 400
        
        # Pixmap oluştur
        pixmap = QPixmap(splash_width, splash_height)
        pixmap.fill(Qt.transparent)
        
        # Gradient arka plan çiz
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Basit gradient oluştur (sadece yeşilden maviye)
        gradient = QLinearGradient(0, 0, splash_width, splash_height)
        gradient.setColorAt(0, QColor(76, 175, 80))  # Yeşil
        gradient.setColorAt(1, QColor(33, 150, 243))  # Mavi
        
        # Arka planı doldur
        painter.fillRect(0, 0, splash_width, splash_height, QBrush(gradient))
        
        # Başlık metni
        painter.setPen(QColor(255, 255, 255))
        title_font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), int(Qt.AlignCenter | Qt.AlignTop), "\n\nMP3 YAP")
        
        # Alt başlık
        subtitle_font = QFont("Arial", 18)
        painter.setFont(subtitle_font)
        painter.drawText(pixmap.rect(), int(Qt.AlignCenter), "\n\n\nYouTube MP3 İndirici")
        
        # Geliştirici bilgisi
        dev_font = QFont("Arial", 12)
        painter.setFont(dev_font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(pixmap.rect(), int(Qt.AlignBottom | Qt.AlignCenter), 
                        "Mehmet Yerli • mehmetyerli.com\n\n")
        
        painter.end()
        
        # Pixmap'i ayarla
        self.setPixmap(pixmap)
        
        # Pencere ayarları
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Opacity efekti
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
        # Fade in animasyonu
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(800)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Fade out animasyonu
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(500)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.on_fade_out_finished)
        
        # Yükleme mesajı
        self.showMessage("Başlatılıyor...", int(Qt.AlignBottom | Qt.AlignCenter), Qt.white)
        
    def start(self):
        """Splash screen'i başlat"""
        self.show()
        self.fade_in_animation.start()
        
        # Mesajları güncelle
        QTimer.singleShot(300, lambda: self.showMessage("Modüller yükleniyor...", 
                         int(Qt.AlignBottom | Qt.AlignCenter), Qt.white))
        QTimer.singleShot(600, lambda: self.showMessage("Ayarlar kontrol ediliyor...", 
                         int(Qt.AlignBottom | Qt.AlignCenter), Qt.white))
        QTimer.singleShot(900, lambda: self.showMessage("Veritabanı hazırlanıyor...", 
                         int(Qt.AlignBottom | Qt.AlignCenter), Qt.white))
        QTimer.singleShot(1200, lambda: self.showMessage("Arayüz oluşturuluyor...", 
                         int(Qt.AlignBottom | Qt.AlignCenter), Qt.white))
        
        # 2 saniye sonra kapat
        QTimer.singleShot(2000, self.fade_out)
        
    def fade_out(self):
        """Fade out animasyonunu başlat"""
        self.fade_out_animation.start()
        
    def on_fade_out_finished(self):
        """Fade out bittiğinde"""
        self.close()
        self.finished.emit()