# MP3Yap Geliştirme Yol Haritası (Roadmap)

Bu dosya, MP3Yap uygulaması için planlanan tüm geliştirmelerin öncelik sırasını ve uygulama takvimini içerir. Tüm detaylı planlar docs klasöründeki ilgili dosyalarda bulunmaktadır.

## 📊 Genel Bakış

| Öncelik | Plan | Dosya | Süre | Zorluk | Durum |
|---------|------|-------|------|---------|--------|
| 1 | Converter Tab İyileştirmeleri | [CONVERTER_TAB_TODO.md](./CONVERTER_TAB_TODO.md) | 1-2 gün | Düşük | 🔵 Bekliyor |
| 2 | Temel UX İyileştirmeleri | [IMPROVEMENTS.md](./IMPROVEMENTS.md#yüksek-öncelikli-i̇yileştirmeler) | 3-5 gün | Düşük-Orta | 🔵 Bekliyor |
| 3 | Modern İkon Sistemi | [IMPROVEMENTS.md](./IMPROVEMENTS.md#115-modern-ikon-sistemi-entegrasyonu) | 2-3 gün | Düşük | 🔵 Bekliyor |
| 4 | Otomatik Güncelleme | [UPDATE_FEATURE_PLAN.md](./UPDATE_FEATURE_PLAN.md) | 4-5 gün | Orta | 🔵 Bekliyor |
| 5 | Çok Dilli Destek | [INTERNATIONALIZATION.md](./INTERNATIONALIZATION.md) | 2-3 hafta | Yüksek | 🔵 Bekliyor |
| 6 | Microsoft Store | [MICROSOFT_STORE_PLAN.md](./MICROSOFT_STORE_PLAN.md) | 1-2 hafta | Orta | ⏸️ İleriki Aşama |
| 7 | Windows Build | [BUILD_WINDOWS.md](./BUILD_WINDOWS.md) | İhtiyaç durumunda | Düşük | ✅ Tamamlandı |

## 🎯 Öncelik 1: Converter Tab İyileştirmeleri

**Dosya:** [CONVERTER_TAB_TODO.md](./CONVERTER_TAB_TODO.md)  
**Süre:** 1-2 gün  
**Zorluk:** Düşük  

### Yapılacaklar:
- [ ] Dropdown'a tıklama ile dosya seçme dialogu açma
- [ ] "Dönüştürülecek dosyaları sürükleyip bırakın" filigranı
- [ ] Hover efektleri ve animasyonlar

### Neden İlk Sırada:
- En basit ve hızlı uygulanabilir
- Kullanıcı deneyimini anında iyileştirir
- Test edilmesi kolay
- Risk içermiyor

## 🎯 Öncelik 2: Temel UX İyileştirmeleri

**Dosya:** [IMPROVEMENTS.md](./IMPROVEMENTS.md#yüksek-öncelikli-i̇yileştirmeler)  
**Süre:** 3-5 gün  
**Zorluk:** Düşük-Orta  

### Yapılacaklar:
- [ ] **Klavye Kısayolları** (1 gün)
  - Ctrl+V: URL yapıştır
  - Ctrl+Enter: Hızlı indirme
  - F5: Yenile
  - Ctrl+H/Q: Sekme değiştirme

- [ ] **İndirme İlerlemesi** (1-2 gün)
  - İndirme hızı gösterimi (KB/s, MB/s)
  - Tahmini kalan süre (ETA)
  - Toplu indirme sayacı

- [ ] **Hata Mesajları** (1 gün)
  - Kullanıcı dostu açıklamalar
  - Çözüm önerileri
  - "Tekrar Dene" butonu

- [ ] **Durum Çubuğu** (1 gün)
  - FFmpeg durumu
  - İnternet bağlantısı
  - Disk alanı göstergesi

### Neden İkinci Sırada:
- Kullanıcıların en çok talep ettiği özellikler
- Uygulamayı profesyonel gösterir
- Mevcut koda entegrasyonu kolay

## 🎯 Öncelik 3: Modern İkon Sistemi

**Dosya:** [IMPROVEMENTS.md](./IMPROVEMENTS.md#115-modern-ikon-sistemi-entegrasyonu)  
**Süre:** 2-3 gün  
**Zorluk:** Düşük  

### Yapılacaklar:
- [ ] Feather Icons entegrasyonu (MIT lisanslı)
- [ ] Tüm emoji'leri SVG ikonlarla değiştir
- [ ] IconManager sınıfı oluştur
- [ ] Dark/Light tema desteği için renk varyantları

### İkon Değişim Listesi:
```
🎵 → music.svg
🎬 → video.svg
📄 → file.svg
⬇️ → download.svg
▶️ → play.svg
⏸️ → pause.svg
✓ → check.svg
🗑️ → trash-2.svg
📁 → folder.svg
🔄 → refresh-cw.svg
⚙️ → settings.svg
```

### Neden Üçüncü Sırada:
- Görsel kaliteyi önemli ölçüde artırır
- Premium ve modern görünüm sağlar
- Platform bağımsız tutarlı görünüm

## 🎯 Öncelik 4: Otomatik Güncelleme

**Dosya:** [UPDATE_FEATURE_PLAN.md](./UPDATE_FEATURE_PLAN.md)  
**Süre:** 4-5 gün  
**Zorluk:** Orta  

### Yapılacaklar:
- [ ] `utils/updater.py` - GitHub API entegrasyonu
- [ ] `ui/update_dialog.py` - Güncelleme bildirimi
- [ ] Config'e güncelleme ayarları
- [ ] Ayarlar dialoguna güncelleme seçenekleri

### Özellikler:
- GitHub Releases API kullanımı
- Otomatik versiyon kontrolü (24 saatte bir)
- Kullanıcı bildirimi ve onayı
- "Sonra Hatırlat" ve "Atla" seçenekleri

### Neden Dördüncü Sırada:
- Kullanıcıların güncel kalmasını sağlar
- Güvenlik ve bug düzeltmeleri için kritik
- GitHub API entegrasyonu nispeten basit

## 🎯 Öncelik 5: Çok Dilli Destek (i18n)

**Dosya:** [INTERNATIONALIZATION.md](./INTERNATIONALIZATION.md)  
**Süre:** 2-3 hafta  
**Zorluk:** Yüksek  

### Yapılacaklar:
- [ ] **Altyapı** (1 hafta)
  - TranslationManager sınıfı
  - QTranslator entegrasyonu
  - Dil değiştirme mekanizması

- [ ] **String Dönüşümü** (1 hafta)
  - ~500+ hardcoded metni self.tr() ile değiştir
  - Context'leri organize et
  - .ts dosyalarını oluştur

- [ ] **İlk Çeviriler** (1 hafta)
  - İngilizce (öncelikli)
  - Almanca
  - Test ve doğrulama

### Desteklenecek Diller:
1. **1. Kademe:** İngilizce, Türkçe, Almanca, İspanyolca, Fransızca
2. **2. Kademe:** Rusça, İtalyanca, Portekizce, Japonca, Çince
3. **3. Kademe:** Arapça (RTL), Korece, Felemenkçe

### Neden Beşinci Sırada:
- En kapsamlı değişiklik
- Global pazara açılmak için kritik
- Uzun vadeli yatırım

## 🎯 Öncelik 6: Microsoft Store Yayını

**Dosya:** [MICROSOFT_STORE_PLAN.md](./MICROSOFT_STORE_PLAN.md)  
**Süre:** 1-2 hafta  
**Zorluk:** Orta  
**Durum:** İleriki aşamada  

### Neden Son Sırada:
- Önce uygulamanın olgunlaşması gerekiyor
- Store gereksinimleri katı
- Maliyet içeriyor ($19 geliştirici hesabı)

## 📅 Haftalık Uygulama Takvimi

### Hafta 1 (3-9 Ocak 2025)
- ✅ Converter Tab TODO'ları tamamla
- ✅ Klavye kısayolları sistemi

### Hafta 2 (10-16 Ocak 2025)
- 📋 İndirme hızı ve ETA gösterimi
- 📋 Hata mesajları iyileştirmesi
- 📋 Durum çubuğu geliştirmeleri

### Hafta 3 (17-23 Ocak 2025)
- 📋 Modern ikon sistemi entegrasyonu
- 📋 Dark/Light tema ikon desteği

### Hafta 4 (24-30 Ocak 2025)
- 📋 Otomatik güncelleme özelliği
- 📋 Test ve bug düzeltmeleri

### Hafta 5-7 (31 Ocak - 20 Şubat 2025)
- 📋 Çok dilli destek altyapısı
- 📋 String dönüşümleri
- 📋 İngilizce ve Almanca çevirileri

## 🏆 Başarı Kriterleri

### Kısa Vadeli (1 Ay)
- [ ] Tüm temel UX iyileştirmeleri tamamlanmış
- [ ] Modern ikon sistemi entegre edilmiş
- [ ] Otomatik güncelleme çalışıyor
- [ ] Kullanıcı geri bildirimleri olumlu

### Orta Vadeli (3 Ay)
- [ ] En az 3 dil desteği aktif
- [ ] Microsoft Store'da yayında
- [ ] Kullanıcı sayısı %50 artmış
- [ ] 4.5+ yıldız rating

### Uzun Vadeli (6 Ay)
- [ ] 10+ dil desteği
- [ ] 100K+ indirme
- [ ] Premium özellikler eklendi
- [ ] Topluluk katkıları aktif

## 📝 Notlar

- Bu roadmap canlı bir dokümandır ve ihtiyaçlara göre güncellenecektir
- Öncelikler kullanıcı geri bildirimlerine göre değişebilir
- Her özellik tamamlandığında durum güncellenecektir
- Detaylı planlar için ilgili dosyalara bakınız

## 🔗 İlgili Dosyalar

- [IMPROVEMENTS.md](./IMPROVEMENTS.md) - Genel iyileştirme önerileri
- [CONVERTER_TAB_TODO.md](./CONVERTER_TAB_TODO.md) - Converter tab özel görevleri
- [INTERNATIONALIZATION.md](./INTERNATIONALIZATION.md) - Çok dilli destek detayları
- [UPDATE_FEATURE_PLAN.md](./UPDATE_FEATURE_PLAN.md) - Otomatik güncelleme planı
- [MICROSOFT_STORE_PLAN.md](./MICROSOFT_STORE_PLAN.md) - Store yayın planı
- [BUILD_WINDOWS.md](./BUILD_WINDOWS.md) - Windows build talimatları

---

*Son güncelleme: 3 Ocak 2025*