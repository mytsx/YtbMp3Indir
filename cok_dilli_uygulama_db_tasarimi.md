# Çok Dilli Masaüstü Uygulama İçin Veritabanı Tasarımı

Bu doküman, MP3Yap uygulamasında tüm metinlerin veritabanından
gelmesini ve çoklu dil desteğini sağlayan **i18n
(internationalization)** yapısını anlatmaktadır.

## 1. Dil Tablosu (languages)

``` sql
CREATE TABLE languages (
    lang_code VARCHAR(10) PRIMARY KEY,    -- 'tr', 'en'
    lang_name VARCHAR(100) NOT NULL,      -- 'Turkish', 'English'
    native_name VARCHAR(100) NOT NULL,    -- 'Türkçe', 'English'
    fallback_lang VARCHAR(10),            -- Fallback dil kodu
    is_rtl INTEGER DEFAULT 0,             -- Sağdan sola yazılan diller için
    is_active INTEGER DEFAULT 1,          -- Aktif/Pasif durumu
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fallback_lang) REFERENCES languages(lang_code)
);
```

## 2. Çeviri Anahtarları Tablosu (translation_keys)

``` sql
CREATE TABLE translation_keys (
    key_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope VARCHAR(100),                   -- Opsiyonel kapsam/bağlam
    key_text VARCHAR(255) NOT NULL,       -- Anahtar metin
    default_text TEXT,                     -- Varsayılan metin (genellikle İngilizce)
    description TEXT,                      -- Çevirmenler için açıklama
    is_active INTEGER DEFAULT 1,          -- Aktif/Pasif durumu
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (scope, key_text)
);
CREATE INDEX idx_translation_keys_scope ON translation_keys(scope);
CREATE INDEX idx_translation_keys_key ON translation_keys(key_text);
```

## 3. Çeviriler Tablosu (translations)

``` sql
CREATE TABLE translations (
    translation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER NOT NULL,              -- Anahtar ID'si
    lang_code VARCHAR(10) NOT NULL,       -- Dil kodu
    translated_text TEXT NOT NULL,        -- Çevrilmiş metin
    status VARCHAR(20) DEFAULT 'approved', -- Çeviri durumu
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (key_id) REFERENCES translation_keys(key_id),
    FOREIGN KEY (lang_code) REFERENCES languages(lang_code),
    UNIQUE (key_id, lang_code)
);
CREATE INDEX idx_translations_key_lang ON translations(key_id, lang_code);
CREATE INDEX idx_translations_lang ON translations(lang_code);
```

## Fallback Mekanizması

Çeviri bulunamadığında şu sırayla fallback yapılır:

``` sql
WITH requested_translation AS (
    SELECT t.translated_text
    FROM translations t
    JOIN translation_keys k ON t.key_id = k.key_id
    WHERE k.key_text = :key 
    AND (k.scope = :scope OR (k.scope IS NULL AND :scope IS NULL))
    AND t.lang_code = :lang_code
),
fallback_translation AS (
    SELECT t.translated_text
    FROM translations t
    JOIN translation_keys k ON t.key_id = k.key_id
    JOIN languages l ON l.lang_code = :lang_code
    WHERE k.key_text = :key
    AND (k.scope = :scope OR (k.scope IS NULL AND :scope IS NULL))
    AND t.lang_code = l.fallback_lang
),
default_translation AS (
    SELECT default_text
    FROM translation_keys
    WHERE key_text = :key
    AND (scope = :scope OR (scope IS NULL AND :scope IS NULL))
)
SELECT COALESCE(
    (SELECT translated_text FROM requested_translation),
    (SELECT translated_text FROM fallback_translation),
    (SELECT default_text FROM default_translation),
    :key  -- Son çare olarak anahtar döndür
)
```

## Uygulama Mimarisi

### TranslationDatabase Sınıfı
- SQLite veritabanı ile çeviri yönetimi
- Önbellekleme mekanizması ile performans optimizasyonu
- Fallback dil desteği
- Toplu içe/dışa aktarma işlemleri

### TranslationManager Sınıfı
- Merkezi çeviri yönetimi singleton
- `tr()` metodu ile kolay çeviri erişimi
- Dil değişikliği sinyalleri
- UI widget'ları için otomatik güncelleme

## İyi Pratikler

- **Anahtar adlandırma**: İngilizce ve açıklayıcı anahtarlar kullan
- **Kapsam kullanımı**: İlgili çevirileri gruplamak için scope kullan
- **Önbellekleme**: Sık kullanılan çeviriler önbellekte tutuluyor
- **Dinamik güncelleme**: `retranslateUi()` metodları ile dil değişikliğinde otomatik güncelleme
- **Performans**: Uygulama başlangıcında veritabanı bağlantısı kurulur
- **Git desteği**: Çeviri veritabanı dosyası versiyon kontrolünde tutulur
