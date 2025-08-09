"""
Çeviri Veritabanı Yöneticisi
Tüm uygulama çevirileri ayrı bir SQLite veritabanında tutulur
"""

import sqlite3
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TranslationDatabase:
    """Çeviri veritabanı yönetim sınıfı"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: Veritabanı dosya yolu. None ise varsayılan kullanılır.
        """
        if db_path is None:
            # Ana veritabanından ayrı bir konum kullan
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(app_dir, 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'translations.db')
        
        self.db_path = db_path
        self._init_database()
        self._cache = {}  # Performans için önbellek
        self._current_language = 'tr'
    
    def _init_database(self):
        """Veritabanı tablolarını oluştur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Dil tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS languages (
                    lang_code TEXT PRIMARY KEY,      -- 'tr', 'en'
                    lang_name TEXT NOT NULL,          -- 'Türkçe', 'English'
                    native_name TEXT NOT NULL,        -- 'Türkçe', 'English'
                    fallback_lang TEXT,               -- Yedek dil kodu
                    is_rtl INTEGER DEFAULT 0,         -- Sağdan sola yazılan diller için
                    is_active INTEGER DEFAULT 1,      -- Aktif/Pasif
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Kaynak anahtar tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translation_keys (
                    key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scope TEXT,                       -- 'main_window', 'settings', vb.
                    key_text TEXT NOT NULL,           -- 'button.download', 'menu.file'
                    description TEXT,                  -- Çevirmenler için açıklama
                    default_text TEXT,                 -- Varsayılan metin (genelde İngilizce)
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(scope, key_text)
                )
            ''')
            
            # Çeviri tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translations (
                    key_id INTEGER NOT NULL,
                    lang_code TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    status TEXT DEFAULT 'approved',   -- 'draft', 'approved', 'rejected'
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    PRIMARY KEY (key_id, lang_code),
                    FOREIGN KEY (key_id) REFERENCES translation_keys(key_id),
                    FOREIGN KEY (lang_code) REFERENCES languages(lang_code)
                )
            ''')
            
            # İndeksler
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_keys_scope ON translation_keys(scope)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_translations_lang ON translations(lang_code)')
            
            # Varsayılan dilleri ekle
            self._insert_default_languages(cursor)
            
            conn.commit()
    
    def _insert_default_languages(self, cursor):
        """Varsayılan dilleri ekle"""
        languages = [
            ('tr', 'Turkish', 'Türkçe', None, 0),
            ('en', 'English', 'English', None, 0)
        ]
        
        for lang in languages:
            cursor.execute('''
                INSERT OR IGNORE INTO languages (lang_code, lang_name, native_name, fallback_lang, is_rtl)
                VALUES (?, ?, ?, ?, ?)
            ''', lang)
    
    def add_translation_key(self, key: str, scope: str = None, description: str = None, 
                           default_text: str = None) -> int:
        """
        Yeni çeviri anahtarı ekle
        
        Args:
            key: Anahtar metni (örn: 'button.download')
            scope: Kapsam (örn: 'main_window')
            description: Açıklama
            default_text: Varsayılan metin
            
        Returns:
            Eklenen kaydın ID'si
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO translation_keys (scope, key_text, description, default_text)
                VALUES (?, ?, ?, ?)
            ''', (scope, key, description, default_text))
            return cursor.lastrowid
    
    def add_translation(self, key: str, lang_code: str, text: str, scope: str = None):
        """
        Çeviri ekle veya güncelle
        
        Args:
            key: Anahtar metni
            lang_code: Dil kodu
            text: Çevrilmiş metin
            scope: Kapsam
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Önce anahtarın ID'sini bul veya oluştur
            cursor.execute('''
                SELECT key_id FROM translation_keys 
                WHERE key_text = ? AND (scope = ? OR (scope IS NULL AND ? IS NULL))
            ''', (key, scope, scope))
            
            result = cursor.fetchone()
            if result:
                key_id = result[0]
            else:
                # Anahtar yoksa oluştur
                cursor.execute('''
                    INSERT INTO translation_keys (scope, key_text, default_text)
                    VALUES (?, ?, ?)
                ''', (scope, key, text if lang_code == 'en' else None))
                key_id = cursor.lastrowid
            
            # Çeviriyi ekle veya güncelle
            cursor.execute('''
                INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text)
                VALUES (?, ?, ?)
            ''', (key_id, lang_code, text))
            
            conn.commit()
            
            # Önbelleği temizle - dil kodunu da dahil et
            # Tüm diller için bu anahtarı temizle
            keys_to_delete = []
            prefix = f"{scope}:{key}" if scope else key
            for cache_key in self._cache:
                if cache_key.endswith(f":{prefix}") or cache_key == prefix:
                    keys_to_delete.append(cache_key)
            for cache_key in keys_to_delete:
                del self._cache[cache_key]
    
    def get_translation(self, key: str, lang_code: str = None, scope: str = None) -> str:
        """
        Çeviri al
        
        Args:
            key: Anahtar metni
            lang_code: Dil kodu (None ise mevcut dil kullanılır)
            scope: Kapsam
            
        Returns:
            Çevrilmiş metin veya anahtar
        """
        if lang_code is None:
            lang_code = self._current_language
        
        # Önbellekte ara
        cache_key = f"{lang_code}:{scope}:{key}" if scope else f"{lang_code}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Çeviriyi al (fallback mekanizması ile)
            cursor.execute('''
                WITH requested_translation AS (
                    SELECT t.translated_text
                    FROM translations t
                    JOIN translation_keys k ON t.key_id = k.key_id
                    WHERE k.key_text = ? 
                    AND (k.scope = ? OR (k.scope IS NULL AND ? IS NULL))
                    AND t.lang_code = ?
                ),
                fallback_translation AS (
                    SELECT t.translated_text
                    FROM translations t
                    JOIN translation_keys k ON t.key_id = k.key_id
                    JOIN languages l ON l.lang_code = ?
                    WHERE k.key_text = ?
                    AND (k.scope = ? OR (k.scope IS NULL AND ? IS NULL))
                    AND t.lang_code = l.fallback_lang
                ),
                default_translation AS (
                    SELECT default_text
                    FROM translation_keys
                    WHERE key_text = ?
                    AND (scope = ? OR (scope IS NULL AND ? IS NULL))
                )
                SELECT COALESCE(
                    (SELECT translated_text FROM requested_translation),
                    (SELECT translated_text FROM fallback_translation),
                    (SELECT default_text FROM default_translation),
                    ?
                )
            ''', (key, scope, scope, lang_code,
                  lang_code, key, scope, scope,
                  key, scope, scope,
                  key))
            
            result = cursor.fetchone()
            text = result[0] if result else key
            
            # Önbelleğe ekle
            self._cache[cache_key] = text
            
            return text
    
    def get_all_translations(self, lang_code: str = None) -> Dict[str, str]:
        """
        Belirli bir dil için tüm çevirileri al
        
        Args:
            lang_code: Dil kodu (None ise mevcut dil)
            
        Returns:
            {anahtar: çeviri} sözlüğü
        """
        if lang_code is None:
            lang_code = self._current_language
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN k.scope IS NOT NULL THEN k.scope || '.' || k.key_text
                        ELSE k.key_text
                    END as full_key,
                    COALESCE(t.translated_text, k.default_text, k.key_text) as text
                FROM translation_keys k
                LEFT JOIN translations t ON k.key_id = t.key_id AND t.lang_code = ?
                WHERE k.is_active = 1
            ''', (lang_code,))
            
            return dict(cursor.fetchall())
    
    def bulk_import_translations(self, translations: Dict[str, Dict[str, str]], scope: str = None):
        """
        Toplu çeviri içe aktarma
        
        Args:
            translations: {anahtar: {dil_kodu: çeviri}} formatında sözlük
            scope: Tüm anahtarlar için kapsam
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for key, langs in translations.items():
                # Önce anahtarın var olup olmadığını kontrol et
                default_text = langs.get('en', list(langs.values())[0] if langs else None)
                cursor.execute('''
                    SELECT key_id FROM translation_keys 
                    WHERE (scope = ? OR (scope IS NULL AND ? IS NULL)) 
                    AND key_text = ?
                ''', (scope, scope, key))
                result = cursor.fetchone()
                
                if result:
                    # Anahtar varsa, key_id'yi al
                    key_id = result[0]
                    # Varolan anahtarın default_text'ini güncelle
                    if default_text:
                        cursor.execute('''
                            UPDATE translation_keys 
                            SET default_text = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE key_id = ?
                        ''', (default_text, key_id))
                else:
                    # Anahtar yoksa, yeni ekle
                    cursor.execute('''
                        INSERT INTO translation_keys (scope, key_text, default_text)
                        VALUES (?, ?, ?)
                    ''', (scope, key, default_text))
                    key_id = cursor.lastrowid
                
                # Çevirileri ekle veya güncelle
                for lang_code, text in langs.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text)
                        VALUES (?, ?, ?)
                    ''', (key_id, lang_code, text))
            
            conn.commit()
            self._cache.clear()  # Önbelleği temizle
    
    def set_language(self, lang_code: str):
        """Mevcut dili değiştir"""
        self._current_language = lang_code
        self._cache.clear()  # Dil değiştiğinde önbelleği temizle
    
    def get_language(self) -> str:
        """Mevcut dili döndür"""
        return self._current_language
    
    def get_available_languages(self) -> List[Tuple[str, str, str]]:
        """
        Mevcut dilleri al
        
        Returns:
            [(kod, ad, yerel_ad)] listesi
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT lang_code, lang_name, native_name
                FROM languages
                WHERE is_active = 1
                ORDER BY lang_code
            ''')
            return cursor.fetchall()
    
    def clear_cache(self):
        """Önbelleği temizle"""
        self._cache.clear()
    
    def get_missing_translations(self, lang_code: str) -> List[str]:
        """
        Eksik çevirileri bul
        
        Args:
            lang_code: Kontrol edilecek dil
            
        Returns:
            Çevirisi olmayan anahtarların listesi
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT k.key_text
                FROM translation_keys k
                LEFT JOIN translations t ON k.key_id = t.key_id AND t.lang_code = ?
                WHERE t.translated_text IS NULL AND k.is_active = 1
            ''', (lang_code,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def export_translations(self, lang_code: str = None) -> Dict:
        """
        Çevirileri dışa aktar
        
        Args:
            lang_code: Dil kodu (None ise tüm diller)
            
        Returns:
            Çeviri sözlüğü
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if lang_code:
                cursor.execute('''
                    SELECT k.key_text, t.translated_text
                    FROM translation_keys k
                    JOIN translations t ON k.key_id = t.key_id
                    WHERE t.lang_code = ? AND k.is_active = 1
                ''', (lang_code,))
                
                return dict(cursor.fetchall())
            else:
                # Tüm dilleri al
                result = {}
                cursor.execute('SELECT lang_code FROM languages WHERE is_active = 1')
                for (lang,) in cursor.fetchall():
                    result[lang] = self.export_translations(lang)
                return result


# Global çeviri veritabanı instance'ı
translation_db = TranslationDatabase()