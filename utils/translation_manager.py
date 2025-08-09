"""Translation Manager for MP3Yap application"""

import os
import locale
from PyQt5.QtCore import QTranslator, QLocale, QCoreApplication, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from typing import Optional, Dict, List


class TranslationManager(QObject):
    """Application translation manager"""
    
    # Signal emitted when language changes
    languageChanged = pyqtSignal(str)
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'native': 'English', 'flag': '🇬🇧', 'rtl': False},
        'tr': {'name': 'Turkish', 'native': 'Türkçe', 'flag': '🇹🇷', 'rtl': False},
        'de': {'name': 'German', 'native': 'Deutsch', 'flag': '🇩🇪', 'rtl': False},
        'es': {'name': 'Spanish', 'native': 'Español', 'flag': '🇪🇸', 'rtl': False},
        'fr': {'name': 'French', 'native': 'Français', 'flag': '🇫🇷', 'rtl': False},
        'ru': {'name': 'Russian', 'native': 'Русский', 'flag': '🇷🇺', 'rtl': False},
        'it': {'name': 'Italian', 'native': 'Italiano', 'flag': '🇮🇹', 'rtl': False},
        'pt': {'name': 'Portuguese', 'native': 'Português', 'flag': '🇵🇹', 'rtl': False},
        'ja': {'name': 'Japanese', 'native': '日本語', 'flag': '🇯🇵', 'rtl': False},
        'zh': {'name': 'Chinese', 'native': '中文', 'flag': '🇨🇳', 'rtl': False},
        'ar': {'name': 'Arabic', 'native': 'العربية', 'flag': '🇸🇦', 'rtl': True},
        'ko': {'name': 'Korean', 'native': '한국어', 'flag': '🇰🇷', 'rtl': False},
        'nl': {'name': 'Dutch', 'native': 'Nederlands', 'flag': '🇳🇱', 'rtl': False},
        'pl': {'name': 'Polish', 'native': 'Polski', 'flag': '🇵🇱', 'rtl': False},
        'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'flag': '🇮🇳', 'rtl': False},
    }
    
    def __init__(self):
        super().__init__()
        self._translator = QTranslator()
        self._qt_translator = QTranslator()  # For Qt's built-in translations
        self._current_language = None
        self._translations_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'translations'
        )
        
        # Create translations directory if it doesn't exist
        os.makedirs(self._translations_path, exist_ok=True)
    
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
                
                # Check for language variants (e.g., pt_BR -> pt)
                if lang_code == 'pt':
                    return 'pt'
                elif lang_code.startswith('zh'):
                    return 'zh'
        except:
            pass
        
        # Default to English if system language is not supported
        return 'en'
    
    def load_language(self, language_code: Optional[str] = None) -> bool:
        """
        Load a language translation
        
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
        
        app = QApplication.instance()
        if not app:
            print("No QApplication instance found")
            return False
        
        # Remove old translator
        if self._current_language:
            app.removeTranslator(self._translator)
            app.removeTranslator(self._qt_translator)
        
        # Load new translation
        translation_file = os.path.join(
            self._translations_path, 
            f"mp3yap_{language_code}.qm"
        )
        
        # Check if translation file exists
        if language_code == 'tr':
            # Turkish is the default language, no translation needed
            # Remove any existing translator
            if self._current_language:
                app.removeTranslator(self._translator)
            print("Using default Turkish language")
        elif os.path.exists(translation_file):
            if self._translator.load(translation_file):
                app.installTranslator(self._translator)
                print(f"Loaded translation: {translation_file}")
            else:
                print(f"Failed to load translation: {translation_file}")
                # Continue anyway - will use default text
        else:
            print(f"Translation file not found: {translation_file}")
            # For other languages, we'll need to generate the translation
        
        # Load Qt's built-in translations (for standard dialogs)
        qt_translation_file = os.path.join(
            self._translations_path,
            f"qtbase_{language_code}.qm"
        )
        if os.path.exists(qt_translation_file):
            if self._qt_translator.load(qt_translation_file):
                app.installTranslator(self._qt_translator)
        
        # Update current language
        self._current_language = language_code
        
        # Set application locale
        locale_obj = QLocale(language_code)
        QLocale.setDefault(locale_obj)
        
        # Handle RTL languages
        if self.SUPPORTED_LANGUAGES[language_code]['rtl']:
            app.setLayoutDirection(2)  # Qt.RightToLeft
        else:
            app.setLayoutDirection(0)  # Qt.LeftToRight
        
        # Emit signal for UI updates
        self.languageChanged.emit(language_code)
        
        return True
    
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
        config.save()
    
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