# YouTube MP3 İndirici 🎵

[![GitHub Release](https://img.shields.io/github/v/release/mytsx/YtbMp3Indir?style=for-the-badge&logo=github&color=brightgreen)](https://github.com/mytsx/YtbMp3Indir/releases/latest)
[![Download](https://img.shields.io/badge/İNDİR-v2.1.0-blue?style=for-the-badge&logo=download)](https://github.com/mytsx/YtbMp3Indir/releases/tag/v2.1.0)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE.txt)

## 📦 Hızlı İndirme

**🚀 [En Son Sürümü İndir (v2.1.0)](https://github.com/mytsx/YtbMp3Indir/releases/tag/v2.1.0)**

Windows için hazırlanmış installer dosyasını indirin ve çalıştırın. Kurulum sırasında MIT lisansını kabul etmeniz gerekmektedir.

---

**Sürüm 2.1** - YouTube videolarını MP3 formatında indirmenizi sağlayan modern ve kullanıcı dostu bir masaüstü uygulaması.

> ✨ **Yeni**: Thread güvenliği iyileştirmeleri, yapılandırılabilir cache yönetimi, gelişmiş kuyruk kontrolü ve performans optimizasyonları!

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
- 🧵 Thread-safe indirme işlemleri (iyileştirilmiş)
- 🔧 Hata yönetimi ve logging
- 📋 Playlist bilgi önizleme
- 🎯 URL eşleşme kontrolü
- 💾 Yapılandırılabilir URL cache yönetimi (100-2000 arası)
- ⚡ Performans optimizasyonları
- 🔒 Gelişmiş bellek yönetimi

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
- Kuyruktan spesifik öğeleri seçerek indirebilirsiniz
- Performans için URL cache boyutunu ayarlayabilirsiniz

### 🗄️ Veritabanı
- Tüm indirme geçmişi SQLite veritabanında saklanır
- Silinen kayıtlar geri getirilebilir (soft delete)
- İndirme istatistikleri otomatik hesaplanır
- Aynı URL'den birden fazla indirme kaydı tutulabilir

#### 🔧 Gelişmiş Özellikler
- **Kuyruk Sistemi**: İndirmeleri sıraya alıp sonra işleyebilir, spesifik öğeleri seçerek indirebilir
- **İptal Özelliği**: İndirmeleri güvenli şekilde durdurup kısmi dosyaları temizler
- **URL Eşleşme**: Daha önce indirilen URL'ler otomatik algılanır
- **Playlist Önizleme**: Liste URL'leri yapıştırınca video sayısı gösterilir
- **Bellek Yönetimi**: URL cache boyutu ayarlanabilir (Ayarlar > Performans)
- **Gelişmiş Arama**: Geçmiş ve kuyruk sekmelerinde arama yapabilir
- **Çoklu Seçim**: Kuyruktan birden fazla öğe seçip indirebilir

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
- Arama ve filtreleme özellikleri
- Spesifik öğeleri indirme (tek veya çoklu seçim)
- Öncelik ayarlama
- Sıralama değiştirme (yukarı/aşağı taşıma)
- Otomatik kuyruk işleme
- Duraklatma ve devam ettirme

## ⚙️ Ayarlar

### İndirme Ayarları
- **Ses Kalitesi**: 128, 192, 320 kbps seçenekleri
- **İndirme Konumu**: Özel klasör seçimi
- **Eşzamanlı İndirme**: 1-5 arası ayarlanabilir
- **Playlist Limiti**: Maksimum video sayısı
- **URL Cache Limiti**: 100-2000 arası ayarlanabilir

### Uygulama Ayarları
- **Tema**: Açık/Koyu tema desteği
- **Bildirimler**: Ses ve klasör açma ayarları
- **Geçmiş Saklama**: 30, 60, 90 gün veya süresiz

## 🐛 Bilinen Sorunlar

- Python 3.13 ile uyumsuzluk (static-ffmpeg kütüphanesi nedeniyle)
- FFmpeg ilk kurulumda internet bağlantısı gerektirir
- Çok büyük playlist'lerde başlangıç yavaşlığı olabilir

## 📄 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır. Detaylar için [LICENSE.txt](LICENSE.txt) dosyasına bakınız.

## 👨‍💻 Geliştirici

**Mehmet Yerli**

- 📧 **İletişim:** [iletisim@mehmetyerli.com](mailto:iletisim@mehmetyerli.com)
- 🌐 **Web Sitesi:** [mehmetyerli.com](https://mehmetyerli.com)
- 💻 **GitHub:** [github.com/mytsx](https://github.com/mytsx)
- 📱 **Bu Proje:** [github.com/mytsx/YtbMp3Indir](https://github.com/mytsx/YtbMp3Indir)

## ⚠️ Sorumluluk Reddi

Bu yazılım hiçbir garanti verilmeksizin "olduğu gibi" sağlanmaktadır. Yazılımın kullanımından doğacak herhangi bir zarar veya hasardan geliştirici sorumlu tutulamaz. Kullanıcılar, indirdikleri içeriklerin telif hakları konusunda sorumludur.

---

<div align="center">

**🎵 Youtube Mp3 İndir - Mehmet Yerli tarafından geliştirilmiştir**

[![GitHub](https://img.shields.io/badge/GitHub-mytsx-black?style=flat&logo=github)](https://github.com/mytsx)
[![Website](https://img.shields.io/badge/Website-mehmetyerli.com-blue?style=flat&logo=globe)](https://mehmetyerli.com)
[![Email](https://img.shields.io/badge/Email-iletisim%40mehmetyerli.com-red?style=flat&logo=gmail)](mailto:iletisim@mehmetyerli.com)

</div>
