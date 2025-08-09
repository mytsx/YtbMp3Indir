"""
Mevcut çevirileri veritabanına aktarma scripti
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.translation_db import translation_db
from utils.translations import TRANSLATIONS


def import_all_translations():
    """Tüm çevirileri veritabanına aktar"""
    
    print("Çeviriler veritabanına aktarılıyor...")
    
    # Toplu içe aktarma için veriyi hazırla
    import_data = {}
    
    for key, translations in TRANSLATIONS.items():
        import_data[key] = translations
    
    # Veritabanına aktar
    translation_db.bulk_import_translations(import_data)
    
    print(f"{len(import_data)} anahtar başarıyla aktarıldı.")
    
    # Kontrol et
    for lang_code in ['tr', 'en']:
        missing = translation_db.get_missing_translations(lang_code)
        if missing:
            print(f"{lang_code} dilinde {len(missing)} eksik çeviri var:")
            for key in missing[:5]:  # İlk 5 eksik anahtarı göster
                print(f"  - {key}")
            if len(missing) > 5:
                print(f"  ... ve {len(missing) - 5} diğer")
        else:
            print(f"{lang_code} dilinde tüm çeviriler mevcut.")
    
    print("\nÇeviri aktarımı tamamlandı!")


if __name__ == "__main__":
    import_all_translations()