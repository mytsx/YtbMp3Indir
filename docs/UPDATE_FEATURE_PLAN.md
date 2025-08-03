# YouTube MP3 İndirici - Otomatik Güncelleme Özelliği Planı

## 1. Güncelleme Yaklaşımı

GitHub Releases API kullanarak güncelleme kontrolü yapacağız. Tam otomatik güncelleme yerine, kullanıcıyı bilgilendirip GitHub release sayfasına yönlendireceğiz (güvenlik ve basitlik için).

## 2. Uygulama Değişiklikleri

### A. Yeni Dosyalar

#### 1. `utils/updater.py` - Güncelleme kontrol mantığı
- GitHub API ile son release kontrolü
- Versiyon karşılaştırma
- QThread ile arka plan kontrolü
- Rate limiting ve hata yönetimi

#### 2. `ui/update_dialog.py` - Güncelleme bildirimi penceresi
- Yeni versiyon bilgileri
- Değişiklik notları gösterimi (Markdown desteği)
- İndir/Sonra Hatırlat/Atla seçenekleri
- Modern ve kullanıcı dostu arayüz

### B. Mevcut Dosya Değişiklikleri

#### 1. `utils/config.py` - Yeni ayarlar:
```python
'check_for_updates': True,           # Otomatik güncelleme kontrolü
'update_check_interval': 24,         # Kontrol sıklığı (saat)
'last_update_check': 0,             # Son kontrol timestamp
'skipped_version': '',              # Atlanan versiyon
```

#### 2. `ui/main_window.py` - Değişiklikler:
- Başlangıçta güncelleme kontrolü (24 saatte bir)
- Menü çubuğuna "Yardım > Güncellemeleri Kontrol Et" seçeneği
- Durum çubuğunda güncelleme ikonu (yeni versiyon varsa)

#### 3. `mp3yap_gui.py` - Versiyon sabiti:
```python
APP_VERSION = "2.2.0"  # Merkezi versiyon tanımı
```

#### 4. `ui/settings_dialog.py` - Güncelleme ayarları:
- "Otomatik güncelleme kontrolü" checkbox
- "Kontrol sıklığı" seçeneği (günlük/haftalık/aylık)
- "Şimdi kontrol et" butonu

## 3. Güncelleme Akışı

### Otomatik Kontrol
1. Uygulama başlangıcında son kontrol zamanı kontrol edilir
2. 24 saat geçmişse, arka planda sessizce kontrol yapılır
3. İnternet bağlantısı yoksa sessizce atlanır
4. Yeni versiyon varsa ve atlanan versiyon değilse bildirim gösterilir

### Manuel Kontrol
1. Yardım menüsünden "Güncellemeleri Kontrol Et" seçilir
2. Hemen kontrol yapılır ve sonuç gösterilir
3. Güncelleme yoksa "Zaten güncel" mesajı

### Bildirim Penceresi
```
┌─────────────────────────────────────┐
│ 🎉 Yeni Güncelleme Mevcut!         │
├─────────────────────────────────────┤
│ Mevcut versiyon: v2.2.0            │
│ Yeni versiyon: v2.3.0              │
│                                     │
│ Yenilikler:                        │
│ • Otomatik güncelleme kontrolü     │
│ • Performans iyileştirmeleri       │
│ • Hata düzeltmeleri               │
│                                     │
│ [İndir] [Sonra Hatırlat] [Atla]   │
└─────────────────────────────────────┘
```

## 4. GitHub API Kullanımı

### API Endpoint
```
GET https://api.github.com/repos/mytsx/YtbMp3Indir/releases/latest
```

### Örnek Response
```json
{
  "tag_name": "v2.3.0",
  "name": "YouTube MP3 İndirici v2.3.0",
  "body": "## Yenilikler\n- Otomatik güncelleme kontrolü\n- ...",
  "html_url": "https://github.com/mytsx/YtbMp3Indir/releases/tag/v2.3.0",
  "assets": [
    {
      "name": "YouTube_MP3_Indirici_v2.3.0_Setup.exe",
      "browser_download_url": "..."
    }
  ]
}
```

### Rate Limiting
- Kimlik doğrulamasız: 60 istek/saat
- Uygulama başına maksimum 1 kontrol/saat
- 403 hatası alınırsa 1 saat bekle

## 5. Güvenlik Önlemleri

1. **HTTPS Zorunlu**: Tüm API çağrıları HTTPS üzerinden
2. **Versiyon Doğrulama**: Semantic versioning kurallarına uygun kontrol
3. **İndirme Yönlendirmesi**: Doğrudan indirme yerine GitHub sayfasına yönlendirme
4. **Hata Yönetimi**: Ağ hataları sessizce loglanır, kullanıcı rahatsız edilmez

## 6. Uygulama Detayları

### UpdateChecker Sınıfı
```python
class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        
    def run(self):
        try:
            # GitHub API çağrısı
            # Versiyon karşılaştırması
            # Signal emit
        except Exception as e:
            logger.error(f"Update check failed: {e}")
```

### Versiyon Karşılaştırma
```python
def compare_versions(current, latest):
    """Semantic versioning karşılaştırması"""
    current_parts = [int(x) for x in current.strip('v').split('.')]
    latest_parts = [int(x) for x in latest.strip('v').split('.')]
    
    for i in range(max(len(current_parts), len(latest_parts))):
        c = current_parts[i] if i < len(current_parts) else 0
        l = latest_parts[i] if i < len(latest_parts) else 0
        if l > c:
            return True
        elif l < c:
            return False
    return False
```

## 7. Test Senaryoları

1. **İlk Çalıştırma**: Güncelleme kontrolü yapılmalı
2. **24 Saat Sonra**: Otomatik kontrol tetiklenmeli
3. **İnternet Yok**: Hata vermeden devam etmeli
4. **Yeni Versiyon**: Bildirim gösterilmeli
5. **Aynı Versiyon**: Sessiz kalmalı
6. **Atlanan Versiyon**: Tekrar gösterilmemeli
7. **Manuel Kontrol**: Anında sonuç vermeli

## 8. Gelecek İyileştirmeler

- **Delta Güncellemeler**: Sadece değişen dosyaları indirme
- **Otomatik Kurulum**: Windows için sessiz kurulum
- **Dijital İmza**: Binary dosyaların imzalanması
- **Rollback**: Eski versiyona dönme özelliği
- **Beta Kanalı**: Test kullanıcıları için erken erişim

## 9. Kullanıcı Deneyimi

- Rahatsız edici olmayan bildirimler
- Güncelleme işlemi kullanıcı kontrolünde
- Açık ve anlaşılır mesajlar
- Hızlı ve güvenilir kontrol mekanizması