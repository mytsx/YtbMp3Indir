# Dönüştürücü Tab İyileştirmeleri - Yapılacaklar

> Not: Bu dosya IMPROVEMENTS.md dosyasındaki genel iyileştirme önerileriyle birlikte değerlendirilmelidir.

## 1. Dropdown'a Tıklama İşlevi
- **Sorun**: Kullanıcı dosya listesi alanına (dropdown/liste widget'ına) tıkladığında hiçbir şey olmuyor
- **Çözüm**: Liste widget'ına tıklandığında otomatik olarak dosya seçme dialogunu aç
- **Uygulama**:
  - `DragDropListWidget` sınıfına `mousePressEvent` override ekle
  - Bu event'te parent widget'ın `select_files()` metodunu çağır
  - Veya `ConverterWidget`'ta `file_list.clicked` sinyalini `select_files()` metoduna bağla

## 2. Filigran/Placeholder Metni
- **Sorun**: Boş liste widget'ı sadece boş bir alan gösteriyor
- **Çözüm**: "Dönüştürülecek dosyaları sürükleyip bırakın" filigranı ekle
- **Uygulama Seçenekleri**:
  
  ### Seçenek 1: Custom Paint Event
  - `DragDropListWidget`'ta `paintEvent` override et
  - Liste boşsa filigran metnini çiz
  - Metin rengi: Gri (#999999)
  - Font: Sistem fontu, italic
  
  ### Seçenek 2: QLabel Overlay
  - Liste widget'ının üzerine bir QLabel yerleştir
  - Liste boşken göster, doluyken gizle
  - Daha basit ama layout yönetimi gerektirir

## 3. Ek İyileştirmeler (Opsiyonel)
- Sürükle-bırak sırasında hover efekti için border rengini değiştir
- Dosya kabul edilebilir olduğunda yeşil, edilemez olduğunda kırmızı border
- Animasyonlu geçişler için QPropertyAnimation kullan

## Kod Örneği (Taslak)

```python
class DragDropListWidget(QListWidget):
    """Sürükle-bırak destekli özel QListWidget"""
    
    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()  # Yeni sinyal
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        
    def mousePressEvent(self, event):
        """Liste'ye tıklandığında dosya seçme dialogunu aç"""
        if self.count() == 0:  # Sadece liste boşsa
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        """Boş liste için filigran çiz"""
        super().paintEvent(event)
        
        if self.count() == 0:
            painter = QPainter(self)
            painter.setPen(QColor(150, 150, 150))
            font = painter.font()
            font.setItalic(True)
            font.setPointSize(12)
            painter.setFont(font)
            
            text = "Dönüştürülecek dosyaları sürükleyip bırakın"
            rect = self.rect()
            painter.drawText(rect, Qt.AlignCenter, text)
```

## Test Senaryoları
1. Boş listeye tıklama → Dosya seçme dialogu açılmalı
2. Dolu listeye tıklama → Normal liste davranışı
3. Filigran metni → Sadece liste boşken görünmeli
4. Sürükle-bırak → Mevcut işlevsellik korunmalı

## 4. Ek İyileştirme Önerileri (Converter Tab'a Özel)

### Kullanıcı Deneyimi
1. **Dosya Önizleme**
   - Seçilen dosyanın metadata bilgilerini göster (süre, bit rate, codec)
   - Küçük bir önizleme player'ı (ilk 10 saniye)
   - Dosya boyutu ve tahmini çıktı boyutu karşılaştırması

2. **Gelişmiş Format Seçenekleri**
   - MP3 dışında diğer ses formatları (AAC, FLAC, OGG)
   - Kalite seçeneği (128k, 192k, 256k, 320k)
   - Özel FFmpeg parametreleri için gelişmiş mod

3. **Toplu İşlem İyileştirmeleri**
   - Klasör seçme ve tüm dosyaları ekleme
   - Alt klasörleri dahil etme seçeneği
   - Dosya filtreleme (sadece video, sadece ses, vb.)

4. **İlerleme Detayları**
   - Her dosya için ayrı ilerleme göstergesi
   - Tahmini kalan süre (ETA)
   - Dönüştürme hızı (2x, 5x realtime gibi)

### Görsel İyileştirmeler
1. **Animasyonlar**
   - Dosya eklendiğinde smooth animasyon
   - Dönüştürme sırasında dönen ikon
   - Başarılı tamamlama için yeşil onay animasyonu

2. **Renk Kodlaması**
   - Bekleyen dosyalar: Gri
   - İşleniyor: Mavi (pulse animasyonu)
   - Tamamlandı: Yeşil
   - Hata: Kırmızı

3. **Detaylı Durum Gösterimi**
   - "Metadata okunuyor..."
   - "Ses akışı çıkarılıyor..."
   - "MP3'e kodlanıyor... %45"
   - "Etiketler yazılıyor..."

### Performans İyileştirmeleri
1. **Paralel İşleme**
   - Çoklu dosya için eş zamanlı dönüştürme
   - CPU çekirdek sayısına göre otomatik ayarlama
   - Kullanıcı tanımlı paralel işlem limiti

2. **Akıllı Kuyruk Yönetimi**
   - Büyük dosyaları önce/sonra işleme seçeneği
   - Hatalı dosyaları otomatik atlama
   - Başarısız dosyaları sonunda tekrar deneme

### Entegrasyon Özellikleri
1. **İndirme Tab'ı ile Entegrasyon**
   - İndirilen videoları otomatik dönüştürme seçeneği
   - İndirme sonrası otomatik MP3'e çevirme kuyruğu

2. **Geçmiş Tab'ı ile Entegrasyon**
   - Dönüştürme geçmişini kaydetme
   - Daha önce dönüştürülen dosyaları işaretleme

3. **Sağ Tık Menüsü**
   - "MP3'e Dönüştür" seçeneği (Windows Explorer entegrasyonu)
   - Hızlı dönüştürme için sistem tray menüsü

### Hata Yönetimi
1. **Detaylı Hata Raporları**
   - FFmpeg çıktısını gösterme seçeneği
   - Hata kodları ve açıklamaları
   - Otomatik hata raporu gönderme

2. **Kurtarma Seçenekleri**
   - Kısmi dönüştürmeleri kaydetme
   - Bozuk dosyaları onarma girişimi
   - Alternatif codec'lerle yeniden deneme

## 5. Uzun Vadeli Özellikler

1. **Ses Düzenleme**
   - Basit kesme/birleştirme araçları
   - Fade in/out efektleri
   - Normalleştirme ve ses seviyesi ayarlama

2. **Metadata Düzenleyici**
   - ID3 tag düzenleme
   - Albüm kapağı ekleme/değiştirme
   - Toplu tag düzenleme

3. **Önizleme ve Karşılaştırma**
   - A/B kalite karşılaştırması
   - Spektrum analizi
   - Bitrate grafiği

4. **Bulut Entegrasyonu**
   - Dönüştürülen dosyaları buluta yükleme
   - Buluttan dosya alma ve dönüştürme
   - Dönüştürme işini bulutta yapma (server-side)