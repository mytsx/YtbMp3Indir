#!/usr/bin/env python3
"""Add missing Turkish translations for keys that only have English."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'translations.db'

# Missing Turkish translations
MISSING_TR_TRANSLATIONS = {
    # Main labels
    "main.labels.paste_urls": "URL'leri Yapıştırın",
    "main.labels.file": "Dosya",
    "main.labels.total": "Toplam",
    "main.labels.waiting": "Bekleyen",
    "main.labels.completed": "Tamamlanan",
    "main.buttons.add_to_queue": "Kuyruğa Ekle",

    # History
    "history.placeholders.search": "Başlık veya kanal adında ara...",
    "history.buttons.refresh": "Yenile",
    "history.buttons.clear": "Temizle",
    "history.columns.format": "Format",
    "history.columns.actions": "İşlemler",
    "history.stats.summary": "Toplam: {} dosya | Boyut: {:.1f} MB | Bugün: {} dosya",

    # Queue
    "queue.menu.clear_completed": "Tamamlananları Temizle",
    "queue.labels.search": "Ara",
    "queue.placeholders.search": "Kuyrukta ara...",
    "queue.labels.filter": "Filtre",
    "queue.filters.all": "Tümü",
    "queue.columns.action": "İşlem",

    # Converter
    "converter.tooltips.delete_original": "Başarılı dönüştürmeden sonra orijinal dosyayı sil",
    "converter.warnings.delete_warning": "Uyarı: Orijinal dosyalar silinecek!",
    "Convert your video, audio and other media files to MP3 format. You can drag and drop files or select them.": "Video, ses ve diğer medya dosyalarınızı MP3 formatına dönüştürün. Dosyaları sürükleyip bırakabilir veya seçebilirsiniz.",

    # Common
    "common.status.loading": "Yükleniyor...",
}


def get_key_id(conn, key_text):
    """Get key_id for a given key_text"""
    cursor = conn.cursor()
    cursor.execute("SELECT key_id FROM translation_keys WHERE key_text = ?", (key_text,))
    result = cursor.fetchone()
    return result[0] if result else None


def add_translation(conn, key_id, lang_code, translated_text):
    """Add a translation"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text, updated_at)
        VALUES (?, ?, ?, datetime('now'))
    """, (key_id, lang_code, translated_text))


def main():
    print("=" * 80)
    print("ADDING MISSING TURKISH TRANSLATIONS")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)

    try:
        added_count = 0
        for key_text, tr_text in MISSING_TR_TRANSLATIONS.items():
            key_id = get_key_id(conn, key_text)

            if key_id:
                add_translation(conn, key_id, 'tr', tr_text)
                print(f"  ✓ Added TR: {key_text}")
                added_count += 1
            else:
                print(f"  ⚠️  Key not found in database: {key_text}")

        conn.commit()
        print(f"\n✅ Successfully added {added_count} Turkish translations!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

    print("=" * 80)


if __name__ == '__main__':
    main()
