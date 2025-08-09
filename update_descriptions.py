#!/usr/bin/env python3
"""
Update descriptions for all translation keys
"""

import sqlite3
from pathlib import Path

def update_all_descriptions():
    """Update descriptions for all translation keys"""
    db_path = Path('data/translations.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all abstract keys
        cursor.execute("""
            SELECT DISTINCT key_text 
            FROM translation_keys 
            WHERE key_text LIKE '%.%'
            ORDER BY key_text
        """)
        
        all_keys = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(all_keys)} abstract keys")
        
        # Generate descriptions based on key structure
        descriptions = {}
        for key in all_keys:
            parts = key.split('.')
            
            # Generate description based on key pattern
            if key.startswith('main.'):
                if 'buttons' in parts:
                    descriptions[key] = f"Ana pencere {parts[-1]} butonu"
                elif 'menu' in parts:
                    descriptions[key] = f"Ana menü {parts[-1]} öğesi"
                elif 'labels' in parts:
                    descriptions[key] = f"Ana pencere {parts[-1]} etiketi"
                elif 'status' in parts:
                    descriptions[key] = f"Durum çubuğu {parts[-1]} mesajı"
                elif 'placeholders' in parts:
                    descriptions[key] = f"Ana pencere {parts[-1]} placeholder metni"
                elif 'window' in parts:
                    descriptions[key] = "Ana pencere başlığı"
                else:
                    descriptions[key] = f"Ana pencere {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('history.'):
                if 'buttons' in parts:
                    descriptions[key] = f"Geçmiş sekmesi {parts[-1]} butonu"
                elif 'columns' in parts:
                    descriptions[key] = f"Geçmiş tablosu {parts[-1]} sütunu"
                elif 'labels' in parts:
                    descriptions[key] = f"Geçmiş sekmesi {parts[-1]} etiketi"
                elif 'title' in parts:
                    descriptions[key] = "Geçmiş sekmesi başlığı"
                else:
                    descriptions[key] = f"Geçmiş sekmesi {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('queue.'):
                if 'buttons' in parts:
                    descriptions[key] = f"Kuyruk sekmesi {parts[-1]} butonu"
                elif 'columns' in parts:
                    descriptions[key] = f"Kuyruk tablosu {parts[-1]} sütunu"
                elif 'status' in parts:
                    descriptions[key] = f"Kuyruk {parts[-1]} durumu"
                elif 'context' in parts:
                    descriptions[key] = f"Kuyruk sağ tık menüsü {parts[-1]} öğesi"
                elif 'labels' in parts:
                    descriptions[key] = f"Kuyruk sekmesi {parts[-1]} etiketi"
                elif 'title' in parts:
                    descriptions[key] = "Kuyruk sekmesi başlığı"
                else:
                    descriptions[key] = f"Kuyruk sekmesi {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('converter.'):
                if 'buttons' in parts:
                    descriptions[key] = f"Dönüştürücü {parts[-1]} butonu"
                elif 'labels' in parts:
                    descriptions[key] = f"Dönüştürücü {parts[-1]} etiketi"
                elif 'status' in parts:
                    descriptions[key] = f"Dönüştürme {parts[-1]} durumu"
                elif 'messages' in parts:
                    descriptions[key] = f"Dönüştürücü {parts[-1]} mesajı"
                elif 'title' in parts:
                    descriptions[key] = "Dönüştürücü sekmesi başlığı"
                else:
                    descriptions[key] = f"Dönüştürücü {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('settings.'):
                if 'window' in parts:
                    descriptions[key] = "Ayarlar penceresi başlığı"
                elif 'tabs' in parts:
                    descriptions[key] = f"Ayarlar {parts[-1]} sekmesi"
                elif 'groups' in parts:
                    descriptions[key] = f"Ayarlar {parts[-1]} grubu"
                elif 'labels' in parts:
                    descriptions[key] = f"Ayarlar {parts[-1]} etiketi"
                elif 'checkboxes' in parts:
                    descriptions[key] = f"Ayarlar {parts[-1]} onay kutusu"
                elif 'tooltips' in parts:
                    descriptions[key] = f"Ayarlar {parts[-1]} ipucu metni"
                elif 'values' in parts:
                    descriptions[key] = f"Ayarlar {parts[-1]} değeri"
                else:
                    descriptions[key] = f"Ayarlar {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('common.'):
                if 'buttons' in parts:
                    descriptions[key] = f"Ortak {parts[-1]} butonu"
                elif 'labels' in parts:
                    descriptions[key] = f"Ortak {parts[-1]} etiketi"
                else:
                    descriptions[key] = f"Ortak {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('dialogs.'):
                if 'titles' in parts:
                    descriptions[key] = f"Dialog {parts[-1]} başlığı"
                elif 'messages' in parts:
                    descriptions[key] = f"Dialog {parts[-1]} mesajı"
                else:
                    descriptions[key] = f"Dialog {' '.join(parts[1:])} öğesi"
                    
            elif key.startswith('shortcuts.'):
                if 'categories' in parts:
                    descriptions[key] = f"Kısayol kategorisi {parts[-1]}"
                else:
                    descriptions[key] = f"Klavye kısayolu {' '.join(parts[1:])}"
                    
            elif key.startswith('splash.'):
                descriptions[key] = f"Açılış ekranı {' '.join(parts[1:])} metni"
                
            elif key.startswith('status.'):
                descriptions[key] = f"Durum mesajı {parts[-1]}"
                
            else:
                # Generic description for unknown patterns
                descriptions[key] = f"{' '.join(parts).replace('_', ' ').title()} öğesi"
        
        # Now add specific descriptions for important keys
        specific_descriptions = {
            "main.buttons.download": "YouTube videosunu MP3 olarak indirme işlemini başlatan buton",
            "main.buttons.download_action": "İndirme sekmesi başlığı ve tab etiketi",
            "main.buttons.paste": "Panodaki URL'yi giriş alanına yapıştıran buton",
            "main.buttons.clear": "URL giriş alanını temizleyen buton",
            "main.buttons.analyze": "Playlist URL'sindeki video sayısını analiz eden buton",
            "main.menu.file": "Dosya menüsü ana başlığı",
            "main.menu.settings": "Ayarlar penceresini açan menü öğesi",
            "main.menu.exit": "Uygulamadan çıkış yapan menü öğesi",
            "main.menu.help": "Yardım menüsü ana başlığı",
            "main.menu.about": "Uygulama hakkında bilgi gösteren menü öğesi",
            "main.menu.keyboard_shortcuts": "Klavye kısayollarını gösteren menü öğesi",
            "main.labels.url": "YouTube URL giriş alanı üzerindeki etiket",
            "main.placeholders.youtube_url": "URL giriş alanında gösterilen yardımcı metin",
            "main.status.ready": "Uygulama hazır durumda olduğunu belirten mesaj",
            "main.status.downloading": "İndirme işlemi devam ederken gösterilen mesaj",
            "main.status.download_complete": "İndirme başarıyla tamamlandığında gösterilen mesaj",
            "main.status.error": "Hata durumunda gösterilen mesaj öneki",
            "main.status.cancelled": "İndirme iptal edildiğinde gösterilen mesaj",
            "main.status.already_downloaded": "Video daha önce indirilmişse gösterilen uyarı",
            "main.status.playlist_detected": "URL'nin playlist olduğu tespit edildiğinde gösterilen mesaj",
            "main.status.analyzing_playlist": "Playlist analiz edilirken gösterilen mesaj",
            "main.status.invalid_url": "Geçersiz YouTube URL'si girildiğinde gösterilen uyarı",
            "main.status.enter_url": "URL girilmesi gerektiğini belirten uyarı",
            
            "history.title": "İndirme geçmişi sekmesinin başlığı",
            "history.labels.search": "Geçmiş arama kutusunun placeholder metni",
            "history.labels.total_downloads": "Toplam indirme sayısını gösteren etiket",
            "history.labels.total_size": "Toplam dosya boyutunu gösteren etiket",
            "history.labels.total_duration": "Toplam video süresini gösteren etiket",
            "history.buttons.clear_history": "Tüm geçmişi temizleyen buton",
            "history.buttons.open_folder": "Dosyanın bulunduğu klasörü açan buton",
            "history.buttons.play": "MP3 dosyasını oynatmak için varsayılan uygulamayı açan buton",
            "history.buttons.redownload": "Seçili videoyu tekrar indiren buton",
            "history.buttons.delete": "Seçili kayıtları geçmişten silen buton",
            
            "queue.title": "İndirme kuyruğu sekmesinin başlığı",
            "queue.labels.queued_items": "Kuyrukta bekleyen öğe sayısını gösteren etiket",
            "queue.labels.active_downloads": "Aktif indirme sayısını gösteren etiket",
            "queue.buttons.pause_all": "Tüm indirmeleri durduran buton",
            "queue.buttons.resume_all": "Duraklatılmış indirmeleri devam ettiren buton",
            "queue.buttons.clear_completed": "Tamamlanmış indirmeleri kuyruktan temizleyen buton",
            "queue.buttons.clear_all": "Tüm kuyruğu temizleyen buton",
            
            "settings.window.title": "Ayarlar penceresinin başlığı",
            "settings.labels.audio_quality": "MP3 ses kalitesi seçim etiketi (128/192/320 kbps)",
            "settings.labels.concurrent_downloads": "Aynı anda yapılabilecek maksimum indirme sayısı",
            "settings.labels.playlist_limit": "Playlist'ten indirilecek maksimum video sayısı",
            "settings.labels.url_cache_limit": "Hafızada tutulacak maksimum URL sayısı",
            "settings.checkboxes.auto_retry": "Başarısız indirmeleri otomatik tekrar deneme seçeneği",
            "settings.checkboxes.notification_sound": "İndirme tamamlandığında ses çalma seçeneği",
            "settings.checkboxes.auto_open_folder": "İndirme sonrası klasörü otomatik açma seçeneği",
            
            "common.buttons.save": "Değişiklikleri kaydeden buton",
            "common.buttons.cancel": "İşlemi iptal eden buton",
            "common.buttons.ok": "Onaylama butonu",
            "common.buttons.browse": "Dosya veya klasör seçim dialogunu açan buton"
        }
        
        # Merge specific descriptions
        descriptions.update(specific_descriptions)
        
        # Update database
        updated_count = 0
        for key, description in descriptions.items():
            cursor.execute("""
                UPDATE translation_keys 
                SET description = ? 
                WHERE key_text = ? AND (description IS NULL OR description LIKE 'Migrated from:%')
            """, (description, key))
            
            if cursor.rowcount > 0:
                updated_count += 1
        
        conn.commit()
        print(f"Updated descriptions for {updated_count} keys")
        
        # Verify the update
        cursor.execute("""
            SELECT COUNT(*) 
            FROM translation_keys 
            WHERE key_text LIKE '%.%' AND description IS NOT NULL AND description NOT LIKE 'Migrated from:%'
        """)
        
        desc_count = cursor.fetchone()[0]
        print(f"Total abstract keys with descriptions: {desc_count}")
        
        # Show sample
        cursor.execute("""
            SELECT key_text, description 
            FROM translation_keys 
            WHERE key_text LIKE '%.%' AND description IS NOT NULL AND description NOT LIKE 'Migrated from:%'
            ORDER BY RANDOM()
            LIMIT 5
        """)
        
        print("\nSample descriptions:")
        for key, desc in cursor.fetchall():
            print(f"  {key}: {desc}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if update_all_descriptions():
        print("\n✓ Successfully updated all descriptions")
    else:
        print("\n✗ Failed to update descriptions")