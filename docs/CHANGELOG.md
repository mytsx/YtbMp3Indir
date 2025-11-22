# Değişiklik Günlüğü

Tüm önemli değişiklikler bu dosyada belgelenecektir.

## [2.2.0] - 2025-08-02

### Yeni Özellikler
- **MP3 Dönüştürücü Sekmesi**: Herhangi bir video veya ses dosyasını MP3'e dönüştürme özelliği eklendi
  - 30+ ses formatı desteği (WAV, FLAC, M4A, OGG, WMA, AAC vb.)
  - Video dosyalarından MP3 çıkarma (MP4, AVI, MKV, MOV vb.)
  - Sürükle-bırak desteği
  - Maksimum kalite 320kbps MP3 çıktısı
  - Akıllı dosya yönetimi (ses dosyaları değiştirilebilir, videolar korunur)
  - İptal edilebilir dönüştürme işlemleri
  - Batch dönüştürme desteği

### İyileştirmeler
- Thread güvenliği iyileştirmeleri
- Gelişmiş hata yönetimi ve logging
- UI performans optimizasyonları (büyük dosya listelerinde)
- Kod kalitesi ve bakım kolaylığı artırıldı
- Windows'ta FFmpeg çalıştırılırken konsol penceresi gizlendi

### Güvenlik
- Dosya isimlerinde HTML injection güvenlik açığı kapatıldı
- Gelişmiş dosya yolu doğrulaması

### Teknik İyileştirmeler
- PyQt5 signal yapısı iyileştirildi (dict tipinde veri geçişi)
- FFmpeg entegrasyonu güçlendirildi (metadata korunumu)
- İptal durumunda kısmi dosya temizliği
- Internationalization (i18n) desteği güçlendirildi

## [2.1.0] - Önceki Sürüm

### Özellikler
- YouTube video ve playlist indirme
- Otomatik MP3 dönüştürme
- İndirme geçmişi ve kuyruk yönetimi
- SQLite veritabanı desteği
- Modern PyQt5 arayüzü