# MP3Yap - Flutter Migration Tasks

PyQt5 uygulamasından Flutter'a geçiş sırasında yapılacak/yapılan işler.

## Tamamlanan Özellikler

- [x] Download Screen (YouTube MP3 indirme)
- [x] History Screen (İndirme geçmişi)
- [x] Settings Screen (Temel ayarlar)
- [x] Queue Screen (Kuyruk yönetimi)
- [x] Player (Müzik çalar)
- [x] Convert Screen (Yerel dosya dönüştürme)
- [x] Download folder selection (İndirme klasörü seçimi)
- [x] Backend auto-start (Backend otomatik başlatma)
- [x] Backend shutdown on app close (Uygulama kapanınca backend durdurma)
- [x] Theme Support (Light/Dark) - Tema desteği
- [x] Splash Screen - Açılış ekranı

## Devam Eden / Planlanan Özellikler

### UI/UX Özellikleri

- [x] Notification sound toggle - Bildirim sesi açma/kapama
- [x] History retention settings - Geçmiş saklama süresi ayarı

### Teknik İyileştirmeler

- [ ] Config persistence (JSON dosyasına kaydetme)
- [ ] i18n (Çoklu dil desteği TR/EN) - En son yapılacak

## Bilinen Sorunlar / TODO

- [ ] macOS App Sandbox entitlements (file picker için gerekebilir)
- [ ] Config değişiklikleri bellekte, restart'ta kaybolur

## Notlar

- Eski PyQt5 kodu: `python_desktop/` klasöründe
- Flutter kodu: `flutter_app/` klasöründe
- Backend: `backend/` klasöründe (FastAPI)
