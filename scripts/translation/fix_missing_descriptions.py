#!/usr/bin/env python3
"""
Fix missing or generic descriptions for translation keys
"""

import sqlite3
from pathlib import Path

# Comprehensive descriptions for all keys
DETAILED_DESCRIPTIONS = {
    # Converter keys
    "converter.description": "Dönüştürücü sekmesinin açıklama metni - dosya seçimi ve sürükle-bırak bilgisi",
    "converter.errors.ffmpeg_message": "FFmpeg bulunamadığında gösterilen detaylı hata mesajı",
    "converter.errors.ffmpeg_title": "FFmpeg hata dialogunun başlığı",
    "converter.labels.drag_drop": "Dosyaları sürükle-bırak alanının üzerindeki bilgi metni",
    "converter.labels.will_be_deleted": "Orijinal dosyaların silineceği uyarı metni",
    "converter.tooltips.delete_original": "Orijinal dosya silme checkbox'ının açıklama balonu",
    "converter.warnings.delete_warning": "Ses dosyalarının silineceği konusundaki önemli uyarı",
    "converter.buttons.cancel": "Dönüştürme işlemini iptal eden buton",
    "converter.buttons.clear_list": "Dönüştürme listesini temizleyen buton",
    "converter.buttons.select_file": "Dosya seçim dialogunu açan buton",
    "converter.buttons.start_conversion": "Dönüştürme işlemini başlatan buton",
    "converter.checkboxes.delete_original": "Dönüştürmeden sonra orijinal dosyayı sil seçeneği",
    
    # Dialogs
    "dialogs.titles.select_files": "Dosya seçim dialogunun pencere başlığı",
    "dialogs.messages.language_change_error": "Dil değiştirme işlemi başarısız olduğunda gösterilen hata mesajı",
    "dialogs.titles.error": "Genel hata dialoglarının başlığı",
    "dialogs.titles.select_folder": "Klasör seçim dialogunun pencere başlığı",
    
    # History
    "history.buttons.delete_selected": "Seçili geçmiş kayıtlarını silen buton",
    "history.columns.downloaded": "İndirme tarihi/zamanı sütunu başlığı",
    "history.columns.file_name": "İndirilen dosya adı sütunu başlığı",
    "history.columns.duration": "Video/ses süresi sütunu başlığı",
    
    # Main window shortcuts
    "shortcuts.categories.general": "Genel kısayollar kategori başlığı",
    "shortcuts.categories.navigation": "Sekmeler arası gezinme kısayolları kategori başlığı",  
    "shortcuts.categories.download": "İndirme işlemleri kısayolları kategori başlığı",
    "shortcuts.general.settings": "Ayarlar penceresini açma kısayolu açıklaması",
    "shortcuts.general.quit": "Uygulamadan çıkış kısayolu açıklaması",
    "shortcuts.general.about": "Hakkında dialogunu açma kısayolu açıklaması",
    "shortcuts.navigation.download_tab": "İndirme sekmesine geçiş kısayolu açıklaması",
    "shortcuts.navigation.history_tab": "Geçmiş sekmesine geçiş kısayolu açıklaması",
    "shortcuts.navigation.queue_tab": "Kuyruk sekmesine geçiş kısayolu açıklaması",
    "shortcuts.navigation.converter_tab": "Dönüştürücü sekmesine geçiş kısayolu açıklaması",
    "shortcuts.download.paste_url": "Panodan URL yapıştırma kısayolu açıklaması",
    "shortcuts.download.clear_url": "URL alanını temizleme kısayolu açıklaması",
    "shortcuts.download.start_download": "İndirmeyi başlatma kısayolu açıklaması",
    
    # Splash screen
    "splash.loading": "Uygulama başlatılırken gösterilen yükleniyor metni",
    "splash.initializing": "Modüller yüklenirken gösterilen başlatılıyor metni",
    
    # Status messages  
    "status.loading": "Genel yükleme durumu göstergesi",
    "status.processing": "İşlem yapılıyor durumu göstergesi",
    "status.success": "İşlem başarılı durumu göstergesi",
    "status.failed": "İşlem başarısız durumu göstergesi",
    
    # Queue specific
    "queue.labels.empty": "Kuyruk boş olduğunda gösterilen bilgi metni",
    "queue.status.processing": "İşleniyor durumu etiketi",
    "queue.columns.actions": "İşlem butonları sütunu başlığı",
    
    # Settings additional
    "settings.labels.download_path": "İndirme klasörü yolu etiketi",
    "settings.labels.max_retries": "Maksimum tekrar deneme sayısı etiketi",
    "settings.tooltips.playlist_limit": "Playlist limiti ayarının açıklama balonu",
    "settings.messages.restart_required": "Ayar değişikliği için yeniden başlatma gerekli uyarısı",
    
    # Common additional
    "common.buttons.ok": "Onaylama/Tamam butonu",
    "common.buttons.close": "Pencereyi kapatma butonu",
    "common.labels.loading": "Yükleniyor göstergesi etiketi",
    "common.labels.please_wait": "Lütfen bekleyin mesajı",
    
    # Main window additional
    "main.window.title": "Ana pencere başlığı - YouTube MP3 İndirici",
    "main.tooltips.url_input": "URL giriş alanının açıklama balonu",
    "main.messages.download_started": "İndirme başladı bilgi mesajı",
    "main.messages.added_to_queue": "Kuyruğa eklendi bilgi mesajı",
    
    # History additional
    "history.tooltips.search": "Arama kutusunun açıklama balonu",
    "history.messages.no_results": "Arama sonucu bulunamadı mesajı",
    "history.labels.filter": "Filtreleme seçenekleri etiketi"
}

def fix_descriptions():
    """Fix missing or generic descriptions"""
    db_path = Path('data/translations.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, get all keys that need better descriptions
        cursor.execute("""
            SELECT key_text, description
            FROM translation_keys
            WHERE key_text LIKE '%.%'
            AND (
                description IS NULL 
                OR description = ''
                OR description LIKE '%öğesi%'
                OR description LIKE 'Added during migration%'
                OR description LIKE '%Migrated from:%'
            )
            ORDER BY key_text
        """)
        
        keys_to_fix = cursor.fetchall()
        print(f"Found {len(keys_to_fix)} keys needing better descriptions")
        
        # Update with detailed descriptions
        updated_count = 0
        for key, old_desc in keys_to_fix:
            if key in DETAILED_DESCRIPTIONS:
                new_desc = DETAILED_DESCRIPTIONS[key]
            else:
                # Generate better description based on key structure
                parts = key.split('.')
                
                if len(parts) >= 2:
                    category = parts[0]
                    subcategory = parts[1] if len(parts) > 1 else ''
                    item = parts[-1]
                    
                    # Create meaningful description
                    if category == 'main':
                        if subcategory == 'buttons':
                            new_desc = f"Ana pencere {item} butonu - İndirme sekmesinde"
                        elif subcategory == 'menu':
                            new_desc = f"Ana menü {item} öğesi"
                        elif subcategory == 'labels':
                            new_desc = f"Ana pencere {item} etiketi"
                        elif subcategory == 'status':
                            new_desc = f"Durum çubuğu {item} mesajı"
                        else:
                            new_desc = f"Ana pencere {item} elementi"
                    
                    elif category == 'history':
                        if subcategory == 'buttons':
                            new_desc = f"Geçmiş sekmesi {item} butonu"
                        elif subcategory == 'columns':
                            new_desc = f"Geçmiş tablosu {item} sütun başlığı"
                        elif subcategory == 'labels':
                            new_desc = f"Geçmiş sekmesi {item} bilgi etiketi"
                        else:
                            new_desc = f"Geçmiş sekmesi {item} elementi"
                    
                    elif category == 'queue':
                        if subcategory == 'buttons':
                            new_desc = f"Kuyruk sekmesi {item} butonu"
                        elif subcategory == 'columns':
                            new_desc = f"Kuyruk tablosu {item} sütun başlığı"
                        elif subcategory == 'status':
                            new_desc = f"Kuyruk {item} durum etiketi"
                        elif subcategory == 'context':
                            new_desc = f"Kuyruk sağ tık menüsü {item} seçeneği"
                        else:
                            new_desc = f"Kuyruk sekmesi {item} elementi"
                    
                    elif category == 'settings':
                        if subcategory == 'labels':
                            new_desc = f"Ayarlar {item} etiketi"
                        elif subcategory == 'checkboxes':
                            new_desc = f"Ayarlar {item} onay kutusu"
                        elif subcategory == 'values':
                            new_desc = f"Ayarlar {item} seçenek değeri"
                        elif subcategory == 'groups':
                            new_desc = f"Ayarlar {item} bölüm başlığı"
                        else:
                            new_desc = f"Ayarlar {item} elementi"
                    
                    elif category == 'converter':
                        if subcategory == 'buttons':
                            new_desc = f"Dönüştürücü {item} butonu"
                        elif subcategory == 'labels':
                            new_desc = f"Dönüştürücü {item} bilgi metni"
                        elif subcategory == 'errors':
                            new_desc = f"Dönüştürücü {item} hata mesajı"
                        else:
                            new_desc = f"Dönüştürücü {item} elementi"
                    
                    else:
                        new_desc = f"{category.title()} {item} elementi"
                else:
                    continue  # Skip non-abstract keys
            
            # Update the description
            cursor.execute("""
                UPDATE translation_keys
                SET description = ?
                WHERE key_text = ?
            """, (new_desc, key))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"  Updated: {key}")
                print(f"    Old: {old_desc}")
                print(f"    New: {new_desc}")
        
        conn.commit()
        print(f"\nTotal updated: {updated_count} descriptions")
        
        # Verify the update
        cursor.execute("""
            SELECT COUNT(*) 
            FROM translation_keys
            WHERE key_text LIKE '%.%'
            AND (
                description IS NULL 
                OR description = ''
                OR description LIKE '%öğesi%'
                OR description LIKE 'Added during migration%'
                OR description LIKE '%Migrated from:%'
            )
        """)
        
        remaining = cursor.fetchone()[0]
        print(f"Remaining keys with generic descriptions: {remaining}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if fix_descriptions():
        print("\n✓ Successfully fixed descriptions")
    else:
        print("\n✗ Failed to fix descriptions")