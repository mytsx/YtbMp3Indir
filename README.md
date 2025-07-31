# YouTube MP3 İndirici 🎵

YouTube videolarını MP3 formatında indirmenizi sağlayan modern ve kullanıcı dostu bir masaüstü uygulaması.

## ✨ Özellikler

- 🎥 YouTube video ve playlist desteği
- 📥 Toplu indirme özelliği (birden fazla URL aynı anda)
- 🔄 Gerçek zamanlı indirme ve dönüştürme durumu takibi
- 🎵 Otomatik MP3 dönüştürme (192 kbps kalitede)
- 📁 Otomatik "music" klasörü oluşturma
- 🖥️ Modern PyQt5 arayüzü
- 🚀 FFmpeg otomatik kurulum (static-ffmpeg ile)

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
2. 🖱️ "İndir" butonuna tıklayın
3. 📊 İndirme ve dönüştürme ilerlemesini takip edin
4. 📁 İndirilen MP3 dosyaları `music/` klasöründe bulunacaktır

## 🔔 Durum Mesajları

Uygulama, işlem durumunu emoji'lerle gösterir:
- 🔗 Bağlantı kontrol ediliyor
- 📥 İndiriliyor
- ✅ İndirme tamamlandı
- 🔄 MP3'e dönüştürülüyor
- ✨ Dönüştürme tamamlandı
- 🎉 Tüm indirmeler tamamlandı

## 📝 Notlar

- İlk çalıştırmada FFmpeg otomatik olarak indirilir (~70MB)
- Playlist URL'leri desteklenir (tüm videolar indirilir)
- Dosya adları otomatik olarak güvenli karakterlere dönüştürülür
- İndirme sırasında uygulama donmaz (thread kullanımı)

## 🐛 Bilinen Sorunlar

- Python 3.13 ile uyumsuzluk (pydub kütüphanesi nedeniyle)
- FFmpeg ilk kurulumda internet bağlantısı gerektirir

## 📄 Lisans

Bu proje açık kaynaklıdır ve kişisel kullanım içindir.
