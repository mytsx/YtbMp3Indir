#!/usr/bin/env python3
"""
Add description column to translation_keys table and populate with descriptions
"""

import sqlite3
from pathlib import Path

# Key descriptions in Turkish (since base language is Turkish)
KEY_DESCRIPTIONS = {
    # Main window buttons and actions
    "main.buttons.download": "YouTube videosunu MP3 olarak indirme butonu",
    "main.buttons.download_action": "İndirme sekmesi başlığı",
    "main.buttons.paste": "Panodan URL yapıştırma butonu",
    "main.buttons.clear": "URL giriş alanını temizleme butonu",
    "main.buttons.analyze": "Playlist URL'sini analiz etme butonu",
    "main.menu.file": "Dosya menüsü başlığı",
    "main.menu.settings": "Ayarlar menü öğesi",
    "main.menu.exit": "Çıkış menü öğesi",
    "main.menu.help": "Yardım menüsü başlığı",
    "main.menu.about": "Hakkında menü öğesi",
    "main.menu.keyboard_shortcuts": "Klavye kısayolları menü öğesi ve dialog başlığı",
    "main.labels.url": "URL giriş alanı etiketi",
    "main.placeholders.youtube_url": "YouTube URL giriş alanı placeholder metni",
    "main.status.ready": "Hazır durumu mesajı",
    "main.status.downloading": "İndirme işlemi devam ediyor mesajı",
    "main.status.download_complete": "İndirme tamamlandı mesajı",
    "main.status.error": "Hata durumu mesajı öneki",
    "main.status.cancelled": "İndirme iptal edildi mesajı",
    "main.status.already_downloaded": "Video zaten indirilmiş uyarısı",
    "main.status.playlist_detected": "Playlist tespit edildi mesajı",
    "main.status.analyzing_playlist": "Playlist analiz ediliyor mesajı",
    "main.status.invalid_url": "Geçersiz YouTube URL'si uyarısı",
    "main.status.enter_url": "URL girilmesi gerektiği uyarısı",
    
    # History widget
    "history.title": "İndirme geçmişi sekmesi başlığı",
    "history.labels.search": "Arama kutusu placeholder metni",
    "history.labels.total_downloads": "Toplam indirme sayısı etiketi",
    "history.labels.total_size": "Toplam dosya boyutu etiketi",
    "history.labels.total_duration": "Toplam süre etiketi",
    "history.buttons.clear_history": "Geçmişi temizleme butonu",
    "history.buttons.open_folder": "Dosya konumunu açma butonu",
    "history.buttons.play": "Dosyayı oynatma butonu",
    "history.buttons.redownload": "Tekrar indirme butonu",
    "history.buttons.delete": "Geçmişten silme butonu",
    "history.columns.title": "Video başlığı sütunu",
    "history.columns.channel": "Kanal adı sütunu",
    "history.columns.duration": "Video süresi sütunu",
    "history.columns.size": "Dosya boyutu sütunu",
    "history.columns.date": "İndirme tarihi sütunu",
    "history.columns.status": "İndirme durumu sütunu",
    
    # Queue widget
    "queue.title": "İndirme kuyruğu sekmesi başlığı",
    "queue.labels.queued_items": "Kuyruktaki öğe sayısı etiketi",
    "queue.labels.active_downloads": "Aktif indirme sayısı etiketi",
    "queue.buttons.pause_all": "Tüm indirmeleri duraklat butonu",
    "queue.buttons.resume_all": "Tüm indirmeleri devam ettir butonu",
    "queue.buttons.clear_completed": "Tamamlananları temizle butonu",
    "queue.buttons.clear_all": "Tüm kuyruğu temizle butonu",
    "queue.columns.title": "Video başlığı sütunu",
    "queue.columns.url": "Video URL'si sütunu",
    "queue.columns.priority": "Öncelik sütunu",
    "queue.columns.status": "İndirme durumu sütunu",
    "queue.columns.progress": "İndirme ilerlemesi sütunu",
    "queue.columns.added": "Eklenme zamanı sütunu",
    "queue.status.waiting": "Bekleme durumu",
    "queue.status.downloading": "İndiriliyor durumu",
    "queue.status.completed": "Tamamlandı durumu",
    "queue.status.failed": "Başarısız durumu",
    "queue.status.paused": "Duraklatıldı durumu",
    "queue.context.remove": "Kuyruktan kaldır menü öğesi",
    "queue.context.retry": "Tekrar dene menü öğesi",
    "queue.context.priority_high": "Yüksek öncelik menü öğesi",
    "queue.context.priority_normal": "Normal öncelik menü öğesi",
    "queue.context.priority_low": "Düşük öncelik menü öğesi",
    
    # Settings dialog
    "settings.window.title": "Ayarlar penceresi başlığı",
    "settings.tabs.download": "İndirme ayarları sekmesi",
    "settings.tabs.application": "Uygulama ayarları sekmesi",
    "settings.groups.audio_settings": "Ses ayarları grup başlığı",
    "settings.groups.download_location": "İndirme konumu grup başlığı",
    "settings.groups.performance": "Performans ayarları grup başlığı",
    "settings.groups.appearance": "Görünüm ayarları grup başlığı",
    "settings.groups.notifications": "Bildirim ayarları grup başlığı",
    "settings.labels.audio_quality": "Ses kalitesi seçim etiketi",
    "settings.labels.concurrent_downloads": "Eşzamanlı indirme sayısı etiketi",
    "settings.labels.playlist_limit": "Playlist indirme limiti etiketi",
    "settings.labels.url_cache_limit": "URL önbellek limiti etiketi",
    "settings.labels.theme": "Tema seçimi etiketi",
    "settings.labels.language": "Dil seçimi etiketi",
    "settings.labels.keep_history": "Geçmiş saklama süresi etiketi",
    "settings.checkboxes.auto_retry": "Başarısız indirmeleri otomatik tekrar dene",
    "settings.checkboxes.notification_sound": "İndirme tamamlandığında ses çal",
    "settings.checkboxes.auto_open_folder": "İndirme sonrası klasörü otomatik aç",
    "settings.tooltips.cache_limit": "URL önbellek limiti açıklaması",
    "settings.values.unlimited": "Sınırsız değeri",
    "settings.values.theme_light": "Açık tema seçeneği",
    "settings.values.theme_dark": "Koyu tema seçeneği",
    "settings.values.history_30_days": "30 gün geçmiş seçeneği",
    "settings.values.history_60_days": "60 gün geçmiş seçeneği",
    "settings.values.history_90_days": "90 gün geçmiş seçeneği",
    "settings.values.history_forever": "Süresiz geçmiş seçeneği",
    
    # Common buttons and labels
    "common.buttons.save": "Kaydet butonu",
    "common.buttons.cancel": "İptal butonu",
    "common.buttons.ok": "Tamam butonu",
    "common.buttons.close": "Kapat butonu",
    "common.buttons.browse": "Gözat butonu (dosya/klasör seçimi)",
    
    # Dialog titles and messages
    "dialogs.titles.confirm": "Onay dialog başlığı",
    "dialogs.titles.error": "Hata dialog başlığı",
    "dialogs.titles.warning": "Uyarı dialog başlığı",
    "dialogs.titles.info": "Bilgi dialog başlığı",
    "dialogs.titles.select_folder": "Klasör seçim dialog başlığı",
    "dialogs.messages.clear_history_confirm": "Geçmişi temizleme onay mesajı",
    "dialogs.messages.clear_queue_confirm": "Kuyruğu temizleme onay mesajı",
    "dialogs.messages.language_change_error": "Dil değiştirme hatası mesajı",
    "dialogs.messages.delete_confirm": "Silme işlemi onay mesajı",
    "dialogs.messages.exit_confirm": "Çıkış onay mesajı (indirmeler devam ederken)",
    
    # Additional status messages
    "status.loading": "Yükleniyor mesajı",
    "status.processing": "İşleniyor mesajı",
    "status.success": "Başarılı işlem mesajı",
    "status.failed": "Başarısız işlem mesajı"
}

def add_description_column():
    """Add description column to translation_keys table"""
    db_path = Path('data/translations.db')
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(translation_keys)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'description' in columns:
            print("Description column already exists")
        else:
            # Add description column
            cursor.execute("""
                ALTER TABLE translation_keys 
                ADD COLUMN description TEXT
            """)
            print("Added description column to translation_keys table")
        
        # Update descriptions for all keys
        updated_count = 0
        for key, description in KEY_DESCRIPTIONS.items():
            cursor.execute("""
                UPDATE translation_keys 
                SET description = ? 
                WHERE key_text = ?
            """, (description, key))
            
            if cursor.rowcount > 0:
                updated_count += 1
        
        conn.commit()
        print(f"Updated descriptions for {updated_count} keys")
        
        # Verify the update
        cursor.execute("""
            SELECT key_text, description 
            FROM translation_keys 
            WHERE description IS NOT NULL 
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
    if add_description_column():
        print("\n✓ Successfully added description column and populated descriptions")
    else:
        print("\n✗ Failed to add description column")