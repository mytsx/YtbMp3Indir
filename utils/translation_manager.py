"""
Merkezi Çeviri Yönetim Sistemi / Centralized Translation Management System
Tüm uygulama çevirileri veritabanından yönetilir
"""

import os
import locale
import logging
from PyQt5.QtCore import QTranslator, QLocale, QCoreApplication, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from typing import Optional, Dict, List

# Configure logging for missing translations
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Önce Python sözlüğünden çevirileri kullan, sonra veritabanına geçeceğiz
try:
    from database.translation_db import translation_db
    USE_DATABASE = True
except ImportError:
    from .translations import TRANSLATIONS
    USE_DATABASE = False


class TranslationManager(QObject):
    """Merkezi çeviri yönetici sınıfı / Centralized translation manager"""
    
    # Signal emitted when language changes
    languageChanged = pyqtSignal(str)
    
    # Supported languages - now just Turkish and English as requested
    SUPPORTED_LANGUAGES = {
        'tr': {'name': 'Turkish', 'native': 'Türkçe', 'flag': '🇹🇷', 'rtl': False},
        'en': {'name': 'English', 'native': 'English', 'flag': '🇬🇧', 'rtl': False},
    }
    
    def __init__(self):
        super().__init__()
        self._translator = QTranslator()
        self._qt_translator = QTranslator()  # For Qt's built-in translations
        self._current_language = 'tr'  # Default to Turkish
        self._translations_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'translations'
        )
        
        # Create translations directory if it doesn't exist
        os.makedirs(self._translations_path, exist_ok=True)
        
        # Veritabanı kullanılıyorsa dili ayarla
        if USE_DATABASE:
            translation_db.set_language(self._current_language)
    
    def tr(self, key: str, *args) -> str:
        """
        Get translation for a key (replaces Qt's tr() method)
        Supports both abstract keys (e.g., "main.buttons.download") and legacy Turkish text keys

        Args:
            key: Translation key (abstract or legacy Turkish text)
            *args: Format arguments if the translation contains placeholders

        Returns:
            Translated text
        """
        if USE_DATABASE:
            # Veritabanından çeviri al (database kendi fallback mekanizmasına sahip)
            text = translation_db.get_translation(key, self._current_language)

            # If translation not found (key returned as-is), log it
            if text == key:
                logger.warning(f"❌ MISSING TRANSLATION: key='{key}' lang='{self._current_language}'")

            # If abstract key not found and it looks like Turkish text (no dots),
            # try as legacy key for backward compatibility
            if text == key and '.' not in key:
                # This might be a legacy Turkish text key
                # The database will handle it if it exists
                pass
        else:
            # Python sözlüğünden çeviri al - database ile aynı fallback mantığı
            if key in TRANSLATIONS:
                trans_dict = TRANSLATIONS[key]
                # Önce istenen dili dene
                if self._current_language in trans_dict:
                    text = trans_dict[self._current_language]
                # Fallback dili dene (İngilizce)
                elif 'en' in trans_dict:
                    text = trans_dict['en']
                    logger.warning(f"⚠️  FALLBACK TO EN: key='{key}' (no {self._current_language})")
                # Son çare olarak anahtarı döndür
                else:
                    text = key
                    logger.warning(f"❌ MISSING TRANSLATION: key='{key}' (no translation found)")
            else:
                text = key
                logger.warning(f"❌ MISSING KEY: '{key}' (not in database)")

        # Format argümanları uygula
        if args:
            try:
                return text.format(*args)
            except (IndexError, KeyError) as e:
                logger.error(f"❌ FORMAT ERROR: key='{key}' args={args} error={e}")
                return text
        return text
    
    def get(self, key: str, *args) -> str:
        """Alias for tr() method"""
        return self.tr(key, *args)
    
    def has_translation(self, key: str) -> bool:
        """Check if a translation exists for a key"""
        if USE_DATABASE:
            return translation_db.has_key(key)
        else:
            return key in TRANSLATIONS
    
    def get_system_language(self) -> str:
        """Get the system's default language"""
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Extract language code (e.g., 'en_US' -> 'en')
                lang_code = system_locale.split('_')[0].lower()

                # Check if we support this language
                if lang_code in self.SUPPORTED_LANGUAGES:
                    return lang_code

                # For Turkish locales
                if lang_code == 'tr':
                    return 'tr'
        except (AttributeError, IndexError, TypeError) as e:
            logger.debug(f"Could not detect system language: {e}")

        # Default to Turkish if system language is not supported
        return 'tr'
    
    def load_language(self, language_code: Optional[str] = None) -> bool:
        """
        Switch to a different language
        
        Args:
            language_code: Language code to load. If None, uses system language.
        
        Returns:
            True if successful, False otherwise
        """
        if language_code is None:
            language_code = self.get_system_language()
        
        # Check if language is supported
        if language_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language: {language_code}")
            return False
        
        # If same language, no need to reload
        if language_code == self._current_language:
            return True
        
        # Update current language
        self._current_language = language_code
        
        # Veritabanı kullanılıyorsa dili güncelle
        if USE_DATABASE:
            translation_db.set_language(language_code)
        
        # Save preference
        self.save_language_preference(language_code)
        
        # Emit signal for UI updates
        self.languageChanged.emit(language_code)

        logger.info(f"Language changed to: {language_code}")
        return True
    
    def set_language(self, language_code: str) -> bool:
        """Set the application language (alias for load_language)"""
        return self.load_language(language_code)
    
    def get_current_language(self) -> str:
        """Get the current language code"""
        return self._current_language or 'tr'
    
    def get_language_name(self, language_code: str, native: bool = True) -> str:
        """
        Get the display name for a language
        
        Args:
            language_code: Language code
            native: If True, returns native name, else English name
        
        Returns:
            Language name
        """
        if language_code in self.SUPPORTED_LANGUAGES:
            lang_info = self.SUPPORTED_LANGUAGES[language_code]
            return lang_info['native'] if native else lang_info['name']
        return language_code
    
    def get_key_description(self, key: str) -> Optional[str]:
        """
        Get the description for a translation key
        
        Args:
            key: Translation key
        
        Returns:
            Description text or None if not found
        """
        if USE_DATABASE:
            return translation_db.get_key_description(key)
        return None
    
    def get_all_keys_with_descriptions(self) -> Dict[str, str]:
        """
        Get all translation keys with their descriptions
        
        Returns:
            Dictionary mapping keys to descriptions
        """
        if USE_DATABASE:
            return translation_db.get_all_keys_with_descriptions()
        return {}
    
    def get_available_languages(self, native: bool = True) -> List[tuple]:
        """
        Get list of available languages
        
        Args:
            native: If True, returns native names, else English names
        
        Returns:
            List of (code, name, flag) tuples
        """
        languages = []
        for code, info in self.SUPPORTED_LANGUAGES.items():
            name = info['native'] if native else info['name']
            flag = info.get('flag', '')
            languages.append((code, name, flag))
        
        # Sort by name
        languages.sort(key=lambda x: x[1])
        return languages
    
    def save_language_preference(self, language_code: str):
        """Save language preference to config"""
        from utils.config import Config
        config = Config()
        config.set('language', language_code)
        config.save_config()
    
    def load_language_from_config(self) -> str:
        """Load language preference from config"""
        from utils.config import Config
        config = Config()
        
        # Get saved language or system language
        saved_language = config.get('language', None)
        if saved_language and saved_language in self.SUPPORTED_LANGUAGES:
            return saved_language
        
        # Use system language as fallback
        return self.get_system_language()


# Global translation manager instance
translation_manager = TranslationManager()