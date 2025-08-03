# Windows Build Talimatları - v2.2.0

Bu doküman Windows için YouTube MP3 İndirici v2.2.0 versiyonunun nasıl derleneceğini açıklar.

## Gereksinimler

1. **Python 3.11** (Python 3.13 ile uyumsuz!)
2. **PyInstaller**: `pip install pyinstaller`
3. **Inno Setup 6** (Installer oluşturmak için)
4. Tüm Python bağımlılıkları: `pip install -r requirements.txt`

## Build Adımları

### 1. Portable Executable Oluşturma

```bash
# Build ve dist klasörlerini temizle
rmdir /s /q build dist

# PyInstaller ile build al
pyinstaller mp3yap.spec
```

Bu komut `dist/Youtube Mp3 İndir/` klasöründe tüm dosyaları oluşturacak.

### 2. Portable Sürümü Test Etme

```bash
cd "dist/Youtube Mp3 İndir"
"Youtube Mp3 İndir.exe"
```

Test edilecek özellikler:
- Splash screen görünüyor mu?
- YouTube indirme çalışıyor mu?
- MP3 dönüştürücü sekmesi çalışıyor mu?
- FFmpeg düzgün çalışıyor mu?

### 3. Installer Oluşturma

1. Inno Setup'ı açın
2. `installer_script.iss` dosyasını açın
3. "Build" > "Compile" seçeneğini tıklayın
4. Installer `installer_output/` klasöründe oluşacak

### 4. GitHub Release'e Yükleme

Oluşan dosyalar:
- `dist/Youtube Mp3 İndir/` - Portable versiyon (ZIP'leyip yükleyin)
- `installer_output/YouTube_MP3_Indirici_v2.2.0_Setup.exe` - Installer

## Notlar

- FFmpeg binary'leri otomatik olarak dahil edilir
- Icon dosyası `assets/icon.ico` kullanılır
- Version bilgisi `version_info.txt` dosyasından alınır
- Console penceresi görünmez (windowed mode)

## Sorun Giderme

### "Module not found" hatası
Tüm bağımlılıkların yüklü olduğundan emin olun:
```bash
pip install -r requirements.txt
```

### FFmpeg bulunamıyor hatası
`static-ffmpeg` paketinin düzgün yüklendiğinden emin olun:
```bash
pip install static-ffmpeg==2.13
```

### Antivirus uyarısı
PyInstaller ile oluşturulan executable'lar bazen yanlış pozitif uyarı verebilir. 
Windows Defender'da istisna ekleyebilirsiniz.