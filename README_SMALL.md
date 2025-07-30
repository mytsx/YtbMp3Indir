# MP3 Yap - Küçük Boyutlu Sürümler

Bu klasörde MP3 Yap uygulamasının daha küçük boyutlu sürümleri bulunmaktadır. Aşağıda her bir sürüm hakkında bilgi verilmiştir.

## Sürümler

### 1. MP3Yap_small

Bu sürüm, orijinal uygulamanın daha küçük boyutlu bir versiyonudur. PyInstaller ile paketlenmiş, ancak gereksiz modüller çıkarılmış ve dosyalar bir klasör içinde toplanmıştır.

- **Avantajları**: Orijinal sürüme göre daha küçük boyutlu
- **Dezavantajları**: Hala bir miktar büyük olabilir
- **Kullanım**: `MP3Yap_small.bat` dosyasını çalıştırın

### 2. MP3Yap_minimal

Bu sürüm, PyQt5 yerine Tkinter kullanarak oluşturulmuş minimal bir sürümdür. Tkinter, Python ile birlikte geldiği için daha az bağımlılık içerir ve daha küçük bir exe dosyası oluşturur.

- **Avantajları**: En küçük boyutlu exe dosyası
- **Dezavantajları**: Arayüz daha basit
- **Kullanım**: `MP3Yap_minimal.bat` dosyasını çalıştırın

### 3. MP3Yap_python

Bu sürüm, exe dosyası içermez ve doğrudan Python betiğini çalıştırır. Bu nedenle bilgisayarınızda Python, PyQt5 ve yt-dlp kurulu olmalıdır.

- **Avantajları**: Hiç exe dosyası yok, sadece betik dosyaları
- **Dezavantajları**: Python ve gerekli kütüphanelerin kurulu olması gerekir
- **Kullanım**: `MP3Yap_python.bat` dosyasını çalıştırın

## Nasıl Oluşturulur?

Eğer kendiniz bu sürümleri oluşturmak isterseniz, aşağıdaki komutları kullanabilirsiniz:

### MP3Yap_small

```
pyinstaller MP3Yap_small.spec
```

### MP3Yap_minimal

```
pyinstaller mp3yap_minimal.spec
```

## Notlar

- Tüm sürümler aynı işlevi görür: YouTube videolarını MP3 formatına dönüştürür.
- İndirilen dosyalar her zaman "music" klasöründe saklanır.
- Herhangi bir sorun yaşarsanız, orijinal sürümü kullanmayı deneyin.
