# Windows Setup Guide

Bu klasör Windows için kurulum dosyalarını içerir.

## Gereksinimler

### Windows'ta Derleme İçin:
1. Python 3.11 (3.13 ile uyumsuzluk var)
2. Visual Studio C++ Build Tools
3. Inno Setup 6 (installer oluşturmak için)

## Kurulum Adımları

### 1. Geliştirme Bağımlılıklarını Yükleyin
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Executable Oluşturun
```bash
python build_windows.py
```

veya

```bash
build.bat
```

Bu komut:
- ICO dosyası oluşturur (PNG'den)
- PyInstaller ile tek bir EXE dosyası oluşturur
- Tüm bağımlılıkları EXE içine paketler

### 3. Installer Oluşturun
1. [Inno Setup](https://jrsoftware.org/isdl.php) programını indirin ve kurun
2. `mp3yap_installer.iss` dosyasını Inno Setup ile açın
3. Build → Compile menüsünden derleyin

veya komut satırından:
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" mp3yap_installer.iss
```

## Çıktılar

- **dist/MP3Yap.exe** - Tek başına çalışabilen executable
- **installer_output/MP3Yap_Setup_2.1.exe** - Windows installer

## Notlar

- PyInstaller Windows'ta en iyi çalışır. Cross-compilation sorunlu olabilir.
- Antivirüs yazılımları PyInstaller ile oluşturulan EXE'leri yanlış pozitif olarak işaretleyebilir.
- EXE boyutu büyük olabilir (50-100 MB) çünkü Python runtime ve tüm kütüphaneler dahildir.

## Temizlik

Build artifaktlarını temizlemek için:
```bash
clean.bat
```