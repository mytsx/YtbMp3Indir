"""
Merkezi Çeviri Yönetim Sistemi / Centralized Translation Management System
Tüm uygulama çevirileri veritabanından yönetilir
"""

import os
import locale
from PyQt5.QtCore import QTranslator, QLocale, QCoreApplication, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from typing import Optional, Dict, List

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
        
        Args:
            key: Translation key
            *args: Format arguments if the translation contains placeholders
            
        Returns:
            Translated text
        """
        if USE_DATABASE:
            # Veritabanından çeviri al
            text = translation_db.get_translation(key, self._current_language)
        else:
            # Python sözlüğünden çeviri al
            if key in TRANSLATIONS:
                text = TRANSLATIONS[key].get(self._current_language, key)
            else:
                text = key
        
        # Format argümanları uygula
        if args:
            try:
                return text.format(*args)
            except (IndexError, KeyError):
                return text
        return text
    
    def get(self, key: str, *args) -> str:
        """Alias for tr() method"""
        return self.tr(key, *args)
    
    def has_translation(self, key: str) -> bool:
        """Check if a translation exists for a key"""
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
        except:
            pass
        
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
            print(f"Unsupported language: {language_code}")
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
        
        print(f"Language changed to: {language_code}")
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