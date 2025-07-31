# YouTube MP3 İndirici 🎵

**Sürüm 2.0** - YouTube videolarını MP3 formatında indirmenizi sağlayan modern ve kullanıcı dostu bir masaüstü uygulaması.

> ✨ **Yeni**: Soft delete, gelişmiş kuyruk sistemi, playlist önizleme, URL otomatik kontrolü ve çok daha fazlası!

## ✨ Özellikler

### 🎵 İndirme Özellikleri
- 🎥 YouTube video ve playlist desteği
- 📥 Toplu indirme özelliği (birden fazla URL aynı anda)
- 🔄 Gerçek zamanlı indirme ve dönüştürme durumu takibi
- 🎵 Otomatik MP3 dönüştürme (192 kbps kalitede)
- 📁 Otomatik "music" klasörü oluşturma
- ⏹ İndirme iptal etme özelliği
- 🔍 URL geçerliliği kontrolü

### 🖥️ Arayüz Özellikleri
- 🖥️ Modern PyQt5 arayüzü
- 🎨 Animasyonlu splash screen
- 📊 İndirme geçmişi yönetimi
- 📋 İndirme kuyruğu sistemi
- ⚙️ Ayarlar paneli
- 🔄 Otomatik URL temizleme

### 🗄️ Veritabanı Özellikleri
- 📊 SQLite veritabanı ile geçmiş takibi
- 🔍 İndirme geçmişinde arama
- 📈 İndirme istatistikleri
- 🗑️ Soft delete (geri getirilebilir silme)
- 💾 Güvenli veri saklama

### 🛠️ Teknik Özellikler
- 🚀 FFmpeg otomatik kurulum (static-ffmpeg ile)
- 🧵 Thread-safe indirme işlemleri
- 🔧 Hata yönetimi ve logging
- 📋 Playlist bilgi önizleme
- 🎯 URL eşleşme kontrolü

## 🛠️ Gereksinimler

- Python 3.11 veya üzeri (Python 3.13 ile uyumsuz)
- Aşağıdaki Python kütüphaneleri:
  - PyQt5
  - yt-dlp
  - static-ffmpeg

## 📦 Kurulum

### 1. Depoyu klonlayın:
```bash
git clone https://github.com/kullaniciadi/mp3yap.git
cd mp3yap
```

### 2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

veya manuel olarak:
```bash
pip install PyQt5==5.15.11 yt-dlp==2025.7.21 static-ffmpeg==2.13
```

## 🚀 Kullanım

### Uygulamayı başlatın:
```bash
python mp3yap_gui.py
```

### Kullanım adımları:
1. 📋 YouTube URL'lerini metin alanına yapıştırın (her URL yeni satırda)
2. 🔍 URL durumu otomatik kontrol edilir ve geçerlilik gösterilir
3. 📊 Playlist URL'leri için video sayısı otomatik gösterilir
4. 🖱️ "İndir" butonuna tıklayın veya "Kuyruğa Ekle" ile sonra indirebilirsiniz
5. 📊 İndirme ve dönüştürme ilerlemesini takip edin
6. ⏹ Gerekirse "İptal" butonu ile durdurun
7. 📁 İndirilen MP3 dosyaları `music/` klasöründe bulunacaktır
8. 📈 "Geçmiş" sekmesinden indirme geçmişinizi görüntüleyin

## 🔔 Durum Mesajları

Uygulama, işlem durumunu emoji'lerle gösterir:
- 🔗 Bağlantı kontrol ediliyor
- 📥 İndiriliyor
- ✅ İndirme tamamlandı / Kaydedildi
- 🔄 MP3'e dönüştürülüyor
- ✨ Dönüştürme tamamlandı
- 🎉 Tüm indirmeler tamamlandı
- ⏳ Playlist bilgisi alınıyor...
- ⚠ Dosya eksik uyarıları
- ✓ Geçerli URL'ler ve mevcut dosyalar

## 📝 Notlar

### 🎯 İndirme İpuçları
- İlk çalıştırmada FFmpeg otomatik olarak indirilir (~70MB)
- Playlist URL'leri desteklenir (video sayısı otomatik gösterilir)
- Dosya adları otomatik olarak güvenli karakterlere dönüştürülür
- İndirme sırasında uygulama donmaz (thread kullanımı)
- URL'ler yapıştırılınca otomatik geçerlilik kontrolü yapılır
- İndirme tamamlandığında URL alanı otomatik temizlenir

### 🗄️ Veritabanı
- Tüm indirme geçmişi SQLite veritabanında saklanır
- Silinen kayıtlar geri getirilebilir (soft delete)
- İndirme istatistikleri otomatik hesaplanır
- Aynı URL'den birden fazla indirme kaydı tutulabilir

### 🔧 Gelişmiş Özellikler
- **Kuyruk Sistemi**: İndirmeleri sıraya alıp sonra işleyebilir
- **İptal Özelliği**: İndirmeleri güvenli şekilde durdurup kısmi dosyaları temizler
- **URL Eşleşme**: Daha önce indirilen URL'ler otomatik algılanır
- **Playlist Önizleme**: Liste URL'leri yapıştırınca video sayısı gösterilir

## 📱 Arayüz Sekmeleri

### 📥 İndirme Sekmesi
- URL giriş alanı (çoklu URL desteği)
- İndirme, iptal, kuyruğa ekle, temizle butonları
- Klasörü aç butonu
- URL durum çubuğu (otomatik kontrol)
- İlerleme çubuğu ve durum göstergesi

### 📊 Geçmiş Sekmesi
- Tüm indirme geçmişi
- Arama özelliği
- İndirme istatistikleri
- Tekrar indirme ve silme butonları
- Tarayıcıda açma özelliği

### 📋 Kuyruk Sekmesi
- İndirme kuyruğu yönetimi
- Öncelik ayarlama
- Sıralama değiştirme
- Otomatik kuyruk işleme

## 🐛 Bilinen Sorunlar

- Python 3.13 ile uyumsuzluk (static-ffmpeg kütüphanesi nedeniyle)
- FFmpeg ilk kurulumda internet bağlantısı gerektirir
- Çok büyük playlist'lerde başlangıç yavaşlığı olabilir

## 📄 Lisans

Bu proje açık kaynaklıdır ve kişisel kullanım içindir.
