# MP3 Yap - YouTube İndirici

Bu uygulama, YouTube videolarını MP3 formatında indirmenizi sağlayan basit bir arayüz sunar.

## Özellikler

- YouTube URL'lerini toplu olarak indirme
- İndirme ilerlemesini görsel olarak takip etme
- İndirilen dosyaları "music" klasörüne kaydetme

## Kullanım

1. Uygulamayı başlatın: `MP3Yap.bat` dosyasına çift tıklayarak veya `dist\MP3Yap.exe` dosyasını çalıştırarak
2. İndirmek istediğiniz YouTube URL'lerini metin alanına yapıştırın (her URL yeni bir satırda olmalıdır)
3. "İndir" butonuna tıklayın
4. İndirme ilerlemesini takip edin
5. İndirilen MP3 dosyaları "music" klasöründe olacaktır

## Gereksinimler

- Python 3.6 veya üzeri
- PyQt5
- yt-dlp

## Kurulum

```bash
pip install PyQt5 yt-dlp
```

## Notlar

- Uygulama, playlist URL'lerini de destekler ve tüm videoları indirir
- İndirilen dosyalar, video başlığına göre adlandırılır
