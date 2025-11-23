# YouTube MP3 İndirici 🎵

[![GitHub Release](https://img.shields.io/github/v/release/mytsx/YtbMp3Indir?style=for-the-badge&logo=github&color=brightgreen)](https://github.com/mytsx/YtbMp3Indir/releases/latest)
[![Download](https://img.shields.io/badge/İNDİR-v2.3.0-blue?style=for-the-badge&logo=download)](https://github.com/mytsx/YtbMp3Indir/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15.11-41CD52?style=for-the-badge&logo=qt)](https://www.riverbankcomputing.com/software/pyqt/)

## 📦 Hızlı İndirme

**🚀 [En Son Sürümü İndir (v2.3.0)](https://github.com/mytsx/YtbMp3Indir/releases/latest)**

Windows için hazırlanmış installer dosyasını indirin ve çalıştırın. Kurulum sırasında MIT lisansını kabul etmeniz gerekmektedir.

---

**Sürüm 2.3** - YouTube videolarını MP3 formatında indirmenizi sağlayan modern ve kullanıcı dostu bir masaüstü uygulaması.

> ✨ **Yeni v2.3.0**: Entegre müzik oynatıcı! İndirdiğiniz MP3'leri geçmiş listesinden çift tıklayarak direkt uygulamada dinleyin. macOS afplay desteği, gerçek zamanlı ilerleme gösterimi ve ses seviyesi kontrolü!

## 📋 İçindekiler

- [✨ Özellikler](#-özellikler)
- [🛠️ Teknik Detaylar](#️-teknik-detaylar)
- [📦 Kurulum](#-kurulum)
- [🚀 Kullanım](#-kullanım)
- [🔮 Gelecek Planlar](#-gelecek-planlar)
- [📄 Lisans](#-lisans)

## ✨ Özellikler

### 🎵 İndirme Özellikleri

- **YouTube İndirme**
  - 🎥 Tekil video indirme
  - 📋 Playlist indirme desteği (otomatik video sayısı tespiti)
  - 📥 Toplu indirme özelliği (birden fazla URL aynı anda)
  - 🎵 Otomatik MP3 dönüştürme (192 kbps kalitede)
  - 🔍 URL geçerliliği kontrolü (gerçek zamanlı)
  - ⏹ İndirme iptal etme ve kısmi dosya temizleme

- **İlerleme Takibi**
  - 🔄 Gerçek zamanlı indirme durumu
  - 📊 İndirme yüzdesi gösterimi
  - 💾 İndirilen/Toplam boyut bilgisi
  - ⚡ Hız ve kalan süre tahmini
  - 📋 Playlist ilerlemesi ([1/10] formatında)

- **Akıllı URL Yönetimi**
  - ✓ Daha önce indirilen URL'leri tanıma
  - 🔗 YouTube URL formatlarını otomatik algılama
  - ⏳ Playlist metadata önizleme
  - 🗑️ Otomatik URL temizleme (indirme sonrası)

### 🎧 Müzik Oynatıcı (YENİ! v2.3.0)

- **Entegre Oynatıcı**
  - 🎵 Geçmiş listesinden çift tıklayarak müzik çalma
  - ⏯️ Play/Pause/Stop kontrolleri
  - 🔊 Ses seviyesi kontrolü (0-100%)
  - ⏱️ Gerçek zamanlı oynatma süresi (0:00 / 5:30 formatında)
  - ✅ Oynatma durumu göstergeleri ("▶ Çalıyor", "⏹ Durduruldu")

- **Teknik Özellikler**
  - 🍎 macOS native afplay entegrasyonu
  - 📊 FFmpeg ile dosya süresi tespiti
  - 🎨 Modern beyaz tema arayüz
  - 🔄 Thread-safe process yönetimi
  - 🗑️ Otomatik kaynak temizleme (uygulama kapanışında)

### 🔄 MP3 Dönüştürücü Özellikleri

- **Format Desteği**
  - 🎵 30+ ses formatı (WAV, FLAC, M4A, OGG, WMA, AAC, AIFF, vb.)
  - 🎬 Video dosyalarından MP3 çıkarma (MP4, AVI, MKV, MOV, WMV, vb.)
  - 📂 Sürükle-bırak desteği
  - 🔊 Maksimum kalite dönüştürme (320kbps)

- **Dosya Yönetimi**
  - 🗑️ Akıllı dosya yönetimi (ses dosyaları değiştirilir, videolar korunur)
  - ⏸️ İptal edilebilir dönüştürme işlemleri
  - 📁 Orijinal dosya konumunda MP3 oluşturma
  - ✅ Toplu dönüştürme desteği

### 🖥️ Arayüz Özellikleri

- **Modern UI/UX**
  - 🖥️ PyQt5 tabanlı modern arayüz
  - 🎨 Animasyonlu splash screen (rastgele renk geçişleri)
  - 📊 Sekme bazlı organizasyon (İndirme/Geçmiş/Kuyruk/Dönüştürücü/Ayarlar)
  - 🎨 Responsive layout ve dinamik boyutlandırma
  - 🔄 Otomatik UI güncellemeleri (signal/slot sistemi)

- **Kullanıcı Deneyimi**
  - 🔍 Canlı arama özellikleri (geçmiş/kuyruk)
  - 📊 Görsel ilerleme göstergeleri
  - 🎯 Renk kodlu durum mesajları
  - ⌨️ Klavye kısayolları desteği
  - 🔔 Durum çubuğu bildirimleri

### 🗄️ Veritabanı Özellikleri

- **SQLite Entegrasyonu**
  - 📊 Tüm indirme geçmişi saklama
  - 🔍 Gelişmiş arama ve filtreleme
  - 📈 İndirme istatistikleri (toplam indirme, boyut, vb.)
  - 🗑️ Soft delete sistemi (geri getirilebilir silme)
  - 💾 Güvenli veri saklama ve transaction yönetimi

- **Kuyruk Yönetimi**
  - 📋 İndirme kuyruğu sistemi
  - 🔢 Öncelik ve pozisyon yönetimi
  - ⏯️ Kuyruk duraklatma/devam ettirme
  - 🔄 Sıralama değiştirme (yukarı/aşağı taşıma)
  - ✓ Çoklu seçim ve toplu işlemler

### 🌍 Çoklu Dil Desteği

- **İnternasyonalizasyon (i18n)**
  - 🇹🇷 Türkçe (varsayılan)
  - 🇬🇧 İngilizce desteği
  - 🗄️ Veritabanı tabanlı çeviri sistemi
  - 🔄 Dinamik dil değiştirme (yeniden başlatma gerektirmez)
  - 📝 Kolay genişletilebilir yapı (yeni diller eklenebilir)

### 🛠️ Gelişmiş Teknik Özellikler

- **Thread Güvenliği**
  - 🧵 Thread-safe indirme işlemleri
  - 🔄 PyQt5 signal/slot sistemi ile güvenli UI güncellemeleri
  - 🔒 Database connection-per-operation pattern
  - ⚡ Asenkron işlem yönetimi

- **Bellek ve Performans**
  - 💾 Yapılandırılabilir URL cache (100-2000 arası)
  - 🚀 Lazy loading ve optimize edilmiş sorgulamalar
  - 🗑️ Otomatik kaynak temizleme
  - 📊 Bellek kullanımı optimizasyonları

- **Hata Yönetimi**
  - 🔧 Kapsamlı logging sistemi
  - ⚠️ Kullanıcı dostu hata mesajları
  - 🔄 Otomatik hata kurtarma mekanizmaları
  - 📝 Debug mode desteği

## 🛠️ Teknik Detaylar

### Mimari

```
mp3yap/
├── mp3yap_gui.py              # Ana entry point
├── core/
│   └── downloader.py          # YouTube indirme motoru (yt-dlp)
├── database/
│   ├── manager.py             # SQLite database yönetimi
│   └── migrations/            # Database migration script'leri
├── ui/
│   ├── main_window.py         # Ana pencere ve tab yönetimi
│   ├── history_widget.py      # Geçmiş sekmesi + müzik oynatıcı
│   ├── queue_widget.py        # Kuyruk yönetimi
│   ├── converter_widget.py    # MP3 dönüştürücü
│   ├── settings_dialog.py     # Ayarlar paneli
│   ├── splash_screen.py       # Başlangıç animasyonu
│   └── music_player_widget.py # Entegre müzik oynatıcı (YENİ!)
├── utils/
│   ├── config.py              # Konfigürasyon yönetimi
│   ├── translation_manager.py # i18n çeviri sistemi
│   └── icon_manager.py        # SVG icon yönetimi
└── styles/
    └── styles.qss             # PyQt5 stylesheet'leri
```

### Teknoloji Stack'i

| Kategori | Teknoloji | Versiyon | Açıklama |
|----------|-----------|----------|----------|
| **Framework** | PyQt5 | 5.15.11 | GUI framework |
| **Python** | Python | 3.11+ | Ana programlama dili |
| **İndirme** | yt-dlp | 2025.7.21 | YouTube indirme motoru |
| **FFmpeg** | static-ffmpeg | 2.13 | MP3 dönüştürme ve audio processing |
| **Database** | SQLite | 3.x | Embedded database |
| **Audio** | afplay | (macOS built-in) | Müzik oynatma (macOS) |
| **Packaging** | requests | >=2.25.0 | HTTP istekleri |

### Önemli Sınıflar ve Metodlar

#### Downloader (core/downloader.py)
```python
class Downloader:
    - download_video(url, output_path)        # Tekil video indirme
    - download_playlist(url)                   # Playlist indirme
    - cancel_download()                        # İndirme iptali
    - progress_hook(d)                         # İlerleme callback'i
```

#### DatabaseManager (database/manager.py)
```python
class DatabaseManager:
    - add_download_history()                   # Geçmişe kayıt
    - get_all_downloads()                      # Tüm kayıtları getir
    - search_history(query)                    # Geçmiş arama
    - add_to_queue()                          # Kuyruğa ekleme
    - soft_delete_record()                    # Kayıt silme (soft)
```

#### MusicPlayerWidget (ui/music_player_widget.py)
```python
class MusicPlayerWidget(QFrame):
    - play_file(file_path)                    # MP3 dosyası oynat
    - toggle_play_pause()                     # Oynatma kontrolü
    - stop_playback()                         # Oynatmayı durdur
    - set_volume(value)                       # Ses seviyesi ayarla
    - update_time_display()                   # Süre güncellemesi
```

#### Signal Sistemi
```python
class DownloadSignals(QObject):
    progress = pyqtSignal(str, float, str)    # İlerleme güncellemesi
    finished = pyqtSignal(str)                 # İndirme tamamlandı
    error = pyqtSignal(str, str)              # Hata oluştu
    status_update = pyqtSignal(str)           # Durum mesajı
    all_downloads_complete = pyqtSignal(bool) # Tüm indirmeler bitti
```

### Database Schema

#### download_history
```sql
CREATE TABLE download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_title TEXT,
    file_name TEXT,
    file_path TEXT,
    url TEXT,
    format TEXT,
    file_size INTEGER,
    duration INTEGER,
    channel_name TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed',
    is_deleted INTEGER DEFAULT 0
);
```

#### download_queue
```sql
CREATE TABLE download_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    video_title TEXT,
    priority INTEGER DEFAULT 0,
    position INTEGER,
    status TEXT DEFAULT 'pending',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    is_deleted INTEGER DEFAULT 0
);
```

#### translation_keys & translations
```sql
-- i18n sistemi için çeviri tabloları
-- 390+ çeviri anahtarı
-- TR ve EN dil desteği
```

## 🔧 Gereksinimler

### Sistem Gereksinimleri

- **İşletim Sistemi**:
  - Windows 10/11
  - macOS 10.14+ (müzik oynatıcı için)
  - Linux (Ubuntu 20.04+)

- **Donanım**:
  - Minimum 4GB RAM
  - 500MB boş disk alanı (FFmpeg dahil)
  - İnternet bağlantısı (ilk kurulum için)

### Python Gereksinimleri

- **Python**: 3.11 veya 3.12 (⚠️ Python 3.13 ile uyumsuz - static-ffmpeg sorunu)
- **pip**: 20.0 veya üzeri

### Bağımlılıklar

```txt
PyQt5==5.15.11           # GUI framework
yt-dlp==2025.7.21        # YouTube downloader
static-ffmpeg==2.13      # FFmpeg bundler
requests>=2.25.0         # HTTP client
packaging>=20.0          # Version parsing

# Test dependencies (opsiyonel)
pytest>=7.0.0
pytest-mock>=3.10.0
```

## 📦 Kurulum

### Yöntem 1: Hızlı Kurulum (Önerilen)

1. **Depoyu klonlayın**:
```bash
git clone https://github.com/mytsx/YtbMp3Indir.git
cd YtbMp3Indir
```

2. **Sanal ortam oluşturun (önerilen)**:
```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. **Bağımlılıkları yükleyin**:
```bash
pip install -r requirements.txt
```

### Yöntem 2: Manuel Kurulum

```bash
pip install PyQt5==5.15.11 yt-dlp==2025.7.21 static-ffmpeg==2.13 requests packaging
```

### FFmpeg Kurulumu

FFmpeg ilk çalıştırmada otomatik olarak indirilir (~70MB). Manuel kurulum için:

```bash
python -c "import static_ffmpeg; static_ffmpeg.add_paths()"
```

## 🚀 Kullanım

### Uygulamayı Başlatma

```bash
python mp3yap_gui.py
```

### VSCode ile Debug

F5 tuşuna basarak debug modda başlatabilirsiniz. `.vscode/launch.json` dosyası şu konfigürasyonları içerir:

- ▶️ MP3Yap: Run App
- 🐛 MP3Yap: Debug Mode (Verbose Logs)
- 🎵 Test: Music Player Widget
- 🧪 Test: All Tests (pytest)

### Kullanım Senaryoları

#### 📥 YouTube Video İndirme

1. Ana sekmede URL alanına YouTube video linkini yapıştırın
2. URL otomatik olarak kontrol edilir (✓ yeşil işaret = geçerli)
3. "İndir" butonuna tıklayın
4. İlerleme çubuğunda indirme durumunu takip edin
5. İndirilen MP3 `music/` klasöründe bulunur

#### 📋 Playlist İndirme

1. YouTube playlist URL'sini yapıştırın
2. Uygulama otomatik olarak video sayısını tespit eder (örn: "10 video tespit edildi")
3. "İndir" veya "Kuyruğa Ekle" seçeneklerini kullanın
4. Her video sırayla indirilir ve ilerleme gösterilir

#### 🎵 Müzik Çalma (YENİ!)

1. "Geçmiş" sekmesine gidin
2. İndirilen bir MP3 dosyasına **çift tıklayın**
3. Müzik oynatıcı otomatik olarak açılır
4. Play/Pause/Stop butonları ile kontrolü sağlayın
5. Ses seviyesini sağdaki slider ile ayarlayın
6. Oynatma süresini gerçek zamanlı takip edin

#### 📋 Kuyruk Yönetimi

1. Birden fazla URL eklemek için "Kuyruğa Ekle" butonunu kullanın
2. "Kuyruk" sekmesinde tüm bekleyen indirmeleri görün
3. Sıralamayı değiştirmek için ↑↓ butonlarını kullanın
4. Öncelik ayarlayın (0-9 arası)
5. İstediğiniz öğeleri seçip "Seçilenleri İndir" ile başlatın

#### 🔄 MP3 Dönüştürme

1. "MP3'e Dönüştür" sekmesine geçin
2. Dosyaları sürükle-bırak yapın veya "Dosya Seç" butonunu kullanın
3. Ses dosyalarını silme seçeneğini ayarlayın
4. "Dönüştürmeyi Başlat" butonuna tıklayın
5. Dönüştürülen MP3'ler orijinal konumda oluşturulur

## ⚙️ Ayarlar

### İndirme Ayarları

| Ayar | Seçenekler | Varsayılan | Açıklama |
|------|-----------|-----------|----------|
| Ses Kalitesi | 128/192/320 kbps | 192 kbps | MP3 bitrate kalitesi |
| İndirme Konumu | Özel klasör | `music/` | İndirilen dosyaların kaydedileceği yer |
| Eşzamanlı İndirme | 1-5 | 1 | Aynı anda kaç indirme yapılacağı |
| Playlist Limiti | 1-100 | 50 | Maksimum playlist video sayısı |
| URL Cache Limiti | 100-2000 | 500 | Bellekte tutulacak URL sayısı |

### Uygulama Ayarları

- **Tema**: Açık/Koyu (gelecek sürümlerde)
- **Bildirimler**: Ses ve klasör açma bildirimleri
- **Geçmiş Saklama**: 30/60/90 gün veya süresiz
- **Otomatik Temizleme**: URL alanını indirme sonrası temizle

### Gelişmiş Ayarlar

- **Debug Mode**: Detaylı log kayıtları
- **Cache Yönetimi**: URL cache boyutu optimizasyonu
- **Database Bakımı**: Veritabanı optimizasyon ayarları

## 🔔 Durum Mesajları ve İkonlar

Uygulama, işlem durumunu emoji'ler ve renkli mesajlarla gösterir:

| Durum | İkon | Renk | Açıklama |
|-------|------|------|----------|
| Kontrol ediliyor | 🔗 | Mavi | URL geçerliliği kontrol ediliyor |
| İndiriliyor | 📥 | Mavi | Video indiriliyor |
| Dönüştürülüyor | 🔄 | Turuncu | MP3'e dönüştürülüyor |
| Tamamlandı | ✅ | Yeşil | İndirme başarılı |
| Hata | ❌ | Kırmızı | İşlem başarısız |
| Playlist | 📋 | Mor | Playlist işleniyor |
| Müzik çalıyor | ▶ | Yeşil | Müzik oynatılıyor |
| Durduruldu | ⏹ | Gri | Oynatma durduruldu |

## 📱 Arayüz Sekmeleri

### 📥 İndirme Sekmesi

- URL giriş alanı (çoklu satır desteği)
- Kontrol butonları:
  - 📥 **İndir**: Hemen indirmeye başla
  - ⏹ **İptal**: Aktif indirmeyi durdur
  - 📋 **Kuyruğa Ekle**: Sonra indirmek üzere kuyruğa al
  - 🗑️ **Temizle**: URL alanını temizle
  - 📁 **Klasörü Aç**: İndirme klasörünü aç
- URL durum çubuğu (gerçek zamanlı geçerlilik göstergesi)
- İlerleme çubuğu ve detaylı durum mesajları

### 📊 Geçmiş Sekmesi

- **İstatistikler**:
  - Toplam indirme sayısı
  - Toplam dosya boyutu
  - En son indirme tarihi

- **Geçmiş Listesi**:
  - Video başlığı ve dosya adı
  - Dosya boyutu ve süre
  - Kanal adı
  - İndirme tarihi ve saati

- **İşlemler**:
  - 🔍 Arama (başlık/kanal/URL)
  - 🔄 Tekrar İndir
  - 🗑️ Sil (soft delete)
  - 🌐 Tarayıcıda Aç
  - 🎵 **Çift Tıkla**: Müzik Oynat (YENİ!)

### 📋 Kuyruk Sekmesi

- **Kuyruk Listesi**:
  - URL ve video başlığı
  - Öncelik seviyesi (0-9)
  - Durum (Bekliyor/İndiriliyor/Tamamlandı)
  - Eklenme tarihi

- **Yönetim Butonları**:
  - ▶️ Seçilenleri İndir
  - ⏸️ Duraklat
  - ▶️ Devam Ettir
  - 🗑️ Kuyruktan Kaldır
  - ⬆️ Yukarı Taşı
  - ⬇️ Aşağı Taşı

- **Filtreleme ve Arama**:
  - Durum bazlı filtreleme
  - Metin arama

### 🔄 MP3 Dönüştürücü Sekmesi

- **Dosya Seçimi**:
  - Sürükle-bırak alanı
  - "Dosya Seç" butonu
  - Desteklenen formatları göster

- **Ayarlar**:
  - Orijinal ses dosyalarını sil checkbox'ı
  - Kalite ayarı (320kbps sabit)

- **İşlemler**:
  - 🔄 Dönüştürmeyi Başlat
  - ⏹ İptal
  - 🗑️ Listeyi Temizle

### ⚙️ Ayarlar Sekmesi

- İndirme ayarları (kalite, konum, vb.)
- Uygulama tercihleri
- Performans ayarları
- Dil seçimi (TR/EN)

## 🔮 Gelecek Planlar

### 🚀 v3.0 - Flutter Migration (Planlanıyor)

Proje, daha modern ve performanslı bir kullanıcı deneyimi için **Flutter Desktop** teknolojisine geçiş yapacak:

#### Hedef Mimari

```
Flutter Frontend (Dart)
        ↕
Unix Domain Socket / Named Pipe (Port çakışması YOK!)
        ↕
FastAPI Backend (Python)
        ↕
Mevcut Core Logic (yt-dlp, FFmpeg, SQLite)
```

#### Planlanan İyileştirmeler

**Frontend (Flutter)**
- ✨ Material Design 3 arayüz
- 🎨 Smooth animasyonlar ve geçişler
- 📱 Responsive ve modern tasarım
- ⚡ Daha hızlı UI render (Skia engine)
- 🎯 Gelişmiş state management (Riverpod)
- 🌈 Özelleştirilebilir temalar

**Backend (FastAPI + Unix Socket)**
- 🚀 %20 daha hızlı iletişim (network stack bypass)
- ✅ SIFIR port çakışması (file system IPC)
- 🔒 Daha güvenli iletişim
- 📡 WebSocket ile real-time updates
- 🔧 REST API ile clean architecture
- 📚 Otomatik API dokümantasyonu (Swagger)

**Teknik Stack**
- Frontend: Flutter 3.x + Riverpod 2.x + Dio 5.x
- Backend: FastAPI 0.104+ + Uvicorn (Unix socket mode)
- Communication: REST API + WebSocket over Unix socket/Named pipe
- Database: aiosqlite (async SQLite wrapper)

**Migration Roadmap**
1. ✅ FastAPI backend API oluşturma (1-2 hafta)
2. ✅ Flutter desktop projesi kurulumu (3-5 gün)
3. ✅ Unix socket adapter implementasyonu
4. ✅ Core features migration (2-3 hafta)
5. ✅ Cross-platform testing (macOS/Windows/Linux)
6. ✅ Production packaging ve deployment

Detaylı migration planı: [`FLUTTER_MIGRATION_PLAN.md`](FLUTTER_MIGRATION_PLAN.md)

### 📋 Kısa Vadeli İyileştirmeler (v2.x)

- [ ] Windows müzik oynatıcı desteği (Windows Media Player API)
- [ ] Linux müzik oynatıcı desteği (GStreamer/VLC)
- [ ] Playlist shuffle/repeat özellikleri
- [ ] Video thumbnail önizleme
- [ ] Karanlık tema desteği (PyQt5)
- [ ] Sistem tray entegrasyonu
- [ ] Global keyboard shortcuts
- [ ] İndirme hızı sınırlayıcı

### 🌟 Uzun Vadeli Hedefler

- [ ] Otomatik güncelleme sistemi
- [ ] Cloud sync (isteğe bağlı)
- [ ] Browser extension entegrasyonu
- [ ] Podcast indirme desteği
- [ ] Spotify/Deezer playlist import
- [ ] Audio normalization özellikleri
- [ ] ID3 tag düzenleme
- [ ] Batch rename tool

## 🐛 Bilinen Sorunlar ve Sınırlamalar

### Mevcut Sorunlar

| Sorun | Platform | Durum | Çözüm |
|-------|----------|-------|-------|
| Python 3.13 uyumsuzluğu | Tümü | 🔴 Bilinen | Python 3.11/3.12 kullanın |
| FFmpeg ilk kurulum yavaşlığı | Tümü | 🟡 Bilinen | İnternet bağlantısı gerekli (~70MB) |
| Büyük playlist başlangıç gecikmesi | Tümü | 🟡 Bilinen | Metadata çekme süreci |
| Müzik oynatıcı sadece macOS | macOS | 🟢 Normal | Windows/Linux desteği gelecek |

### Sınırlamalar

- **FFmpeg Dependency**: static-ffmpeg Python 3.13'te çalışmıyor
- **Müzik Oynatıcı**: Şu an sadece macOS (afplay) desteği var
- **Playlist Boyutu**: Çok büyük playlistler (500+) yavaşlık yaratabilir
- **Eşzamanlı İndirme**: Maximum 5 paralel indirme (performans nedeniyle)

### Troubleshooting

**Problem: FFmpeg bulunamadı**
```bash
# Çözüm: Manuel kurulum
pip install --upgrade static-ffmpeg
python -c "import static_ffmpeg; static_ffmpeg.add_paths()"
```

**Problem: Database kilitleniyor**
```bash
# Çözüm: Database dosyasını yeniden oluştur
rm mp3yap.db
python mp3yap_gui.py  # Otomatik yeniden oluşturulur
```

**Problem: Müzik çalmıyor (macOS)**
```bash
# Çözüm: afplay kontrolü
which afplay  # /usr/bin/afplay çıktısı vermeli
```

## 📊 Proje İstatistikleri

- **Toplam Kod Satırı**: ~8,000+ satır
- **Python Modülleri**: 15+
- **UI Komponenti**: 7 ana widget
- **Database Tabloları**: 4 ana tablo
- **Translation Keys**: 390+ anahtar
- **Desteklenen Diller**: 2 (TR, EN)
- **Test Coverage**: %70+ (hedef: %90)

## 📄 Lisans

Bu proje **MIT Lisansı** altında dağıtılmaktadır. Detaylar için [LICENSE.txt](LICENSE.txt) dosyasına bakınız.

### MIT Lisansı Özeti

✅ Ticari kullanım
✅ Değiştirebilirsiniz
✅ Dağıtabilirsiniz
✅ Özel kullanım
❌ Sorumluluk yok
❌ Garanti yok

## 👨‍💻 Geliştirici

**Mehmet Yerli**

- 📧 **İletişim:** [iletisim@mehmetyerli.com](mailto:iletisim@mehmetyerli.com)
- 🌐 **Web Sitesi:** [mehmetyerli.com](https://mehmetyerli.com)
- 💻 **GitHub:** [@mytsx](https://github.com/mytsx)
- 📱 **Bu Proje:** [github.com/mytsx/YtbMp3Indir](https://github.com/mytsx/YtbMp3Indir)

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. 🍴 Projeyi fork edin
2. 🌿 Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. 💾 Değişikliklerinizi commit edin (`git commit -m 'feat: Add amazing feature'`)
4. 📤 Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. 🔀 Pull Request açın

### Commit Mesaj Formatı

```
<type>: <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Örnek**:
```
feat: Add music player widget with afplay support

- Implement play/pause/stop controls
- Add volume slider with percentage display
- Show real-time playback progress
- Support macOS afplay integration
```

## 🙏 Teşekkürler

Bu proje şu harika açık kaynak projelerden yararlanmaktadır:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube indirme motoru
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing
- [static-ffmpeg](https://github.com/zackees/static-ffmpeg) - FFmpeg bundler

## ⚠️ Sorumluluk Reddi

Bu yazılım hiçbir garanti verilmeksizin **"olduğu gibi"** sağlanmaktadır. Yazılımın kullanımından doğacak herhangi bir zarar veya hasardan geliştirici sorumlu tutulamaz.

**Önemli**: Kullanıcılar, indirdikleri içeriklerin telif hakları konusunda sorumludur. Bu yazılım yalnızca eğitim amaçlıdır ve telif hakkıyla korunan içeriklerin yasadışı indirilmesini teşvik etmez.

## 📚 Dokümantasyon

- 📖 [Kullanım Kılavuzu](docs/USER_GUIDE.md) (yakında)
- 🏗️ [Mimari Dokümantasyonu](docs/ARCHITECTURE.md) (yakında)
- 🔌 [API Referansı](docs/API.md) (v3.0'da)
- 🚀 [Flutter Migration Planı](FLUTTER_MIGRATION_PLAN.md) ✅

## 📞 Destek

Sorularınız veya sorunlarınız için:

- 🐛 **Bug Report**: [GitHub Issues](https://github.com/mytsx/YtbMp3Indir/issues)
- 💡 **Feature Request**: [GitHub Discussions](https://github.com/mytsx/YtbMp3Indir/discussions)
- 📧 **Email**: iletisim@mehmetyerli.com

---

<div align="center">

**🎵 YouTube MP3 İndirici - Mehmet Yerli tarafından ❤️ ile geliştirilmiştir**

[![GitHub](https://img.shields.io/badge/GitHub-mytsx-black?style=flat&logo=github)](https://github.com/mytsx)
[![Website](https://img.shields.io/badge/Website-mehmetyerli.com-blue?style=flat&logo=globe)](https://mehmetyerli.com)
[![Email](https://img.shields.io/badge/Email-iletisim%40mehmetyerli.com-red?style=flat&logo=gmail)](mailto:iletisim@mehmetyerli.com)

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

</div>
