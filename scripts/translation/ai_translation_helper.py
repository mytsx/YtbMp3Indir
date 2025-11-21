#!/usr/bin/env python3
"""
Helper script for AI models to add new language translations
This script provides the interface for AI models to understand and translate the application
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Tuple

class AITranslationHelper:
    """Helper class for AI-assisted translation"""
    
    def __init__(self, db_path: str = 'data/translations.db'):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
    
    def get_keys_for_translation(self, target_language: str) -> List[Tuple[str, str, str]]:
        """
        Get all keys that need translation with their descriptions and base translations
        
        Args:
            target_language: Target language code (e.g., 'en', 'de', 'es')
        
        Returns:
            List of tuples: (key, description, turkish_text)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all abstract keys with descriptions and Turkish translations
            cursor.execute("""
                SELECT 
                    k.key_text,
                    k.description,
                    t.translated_text as turkish_text
                FROM translation_keys k
                LEFT JOIN translations t ON k.key_id = t.key_id AND t.lang_code = 'tr'
                WHERE k.key_text LIKE '%.%'
                AND k.description IS NOT NULL
                AND k.description NOT LIKE 'Migrated from:%'
                ORDER BY k.key_text
            """)
            
            return cursor.fetchall()
    
    def add_language_if_not_exists(self, lang_code: str, lang_name: str, native_name: str):
        """
        Add a new language to the database if it doesn't exist
        
        Args:
            lang_code: Language code (e.g., 'en')
            lang_name: Language name in English (e.g., 'English')
            native_name: Language name in native script (e.g., 'English')
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if language exists
            cursor.execute("SELECT lang_code FROM languages WHERE lang_code = ?", (lang_code,))
            if cursor.fetchone():
                print(f"Language {lang_code} already exists")
                return
            
            # Add new language
            cursor.execute("""
                INSERT INTO languages (lang_code, lang_name, native_name, is_rtl, fallback_lang, is_active)
                VALUES (?, ?, ?, 0, 'tr', 1)
            """, (lang_code, lang_name, native_name))
            
            conn.commit()
            print(f"Added language: {lang_code} ({lang_name})")
    
    def add_translations(self, lang_code: str, translations: Dict[str, str]):
        """
        Add translations for a specific language
        
        Args:
            lang_code: Language code
            translations: Dictionary mapping keys to translated text
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            added = 0
            updated = 0
            
            for key, translated_text in translations.items():
                # Get key_id
                cursor.execute("SELECT key_id FROM translation_keys WHERE key_text = ?", (key,))
                result = cursor.fetchone()
                
                if not result:
                    print(f"Warning: Key not found: {key}")
                    continue
                
                key_id = result[0]
                
                # Check if translation exists
                cursor.execute("""
                    SELECT translation_id FROM translations 
                    WHERE key_id = ? AND lang_code = ?
                """, (key_id, lang_code))
                
                if cursor.fetchone():
                    # Update existing
                    cursor.execute("""
                        UPDATE translations 
                        SET translated_text = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE key_id = ? AND lang_code = ?
                    """, (translated_text, key_id, lang_code))
                    updated += 1
                else:
                    # Insert new
                    cursor.execute("""
                        INSERT INTO translations (key_id, lang_code, translated_text, is_verified)
                        VALUES (?, ?, ?, 0)
                    """, (key_id, lang_code, translated_text))
                    added += 1
            
            conn.commit()
            print(f"Added {added} new translations, updated {updated} existing translations")
    
    def export_for_ai_translation(self, output_file: str = 'translations_for_ai.json'):
        """
        Export translation data in a format suitable for AI translation
        
        Args:
            output_file: Output JSON file path
        """
        keys_data = self.get_keys_for_translation('en')  # Get for any new language
        
        export_data = {
            "instructions": "Translate the Turkish text to your target language. Use the key and description to understand context.",
            "target_language": "SPECIFY_TARGET_LANGUAGE",
            "translations": []
        }
        
        for key, description, turkish_text in keys_data:
            export_data["translations"].append({
                "key": key,
                "description": description or "No description available",
                "turkish_text": turkish_text or "",
                "translated_text": ""  # AI should fill this
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"Exported {len(keys_data)} keys to {output_file}")
    
    def import_ai_translations(self, input_file: str, lang_code: str, lang_name: str, native_name: str):
        """
        Import translations from AI-generated JSON file
        
        Args:
            input_file: Path to JSON file with translations
            lang_code: Language code for the translations
            lang_name: Language name in English
            native_name: Language name in native script
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add language if needed
        self.add_language_if_not_exists(lang_code, lang_name, native_name)
        
        # Prepare translations dictionary
        translations = {}
        for item in data["translations"]:
            if item.get("translated_text"):
                translations[item["key"]] = item["translated_text"]
        
        # Add translations
        self.add_translations(lang_code, translations)
        
        print(f"Imported {len(translations)} translations for {lang_code}")

def main():
    """Example usage"""
    helper = AITranslationHelper()
    
    # Export data for AI translation
    print("Exporting translation data for AI...")
    helper.export_for_ai_translation('translations_for_ai.json')
    
    print("\n" + "="*50)
    print("AI Translation Instructions:")
    print("="*50)
    print("1. Open 'translations_for_ai.json'")
    print("2. Set 'target_language' to your language code (e.g., 'en', 'de', 'es')")
    print("3. Fill in 'translated_text' for each entry")
    print("4. Use the 'description' field to understand the context")
    print("5. Save the file")
    print("6. Run: python ai_translation_helper.py --import <file> <lang_code> <lang_name> <native_name>")
    print("\nExample:")
    print("  python ai_translation_helper.py --import translations_en.json en English English")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--import':
        if len(sys.argv) != 6:
            print("Usage: python ai_translation_helper.py --import <file> <lang_code> <lang_name> <native_name>")
            sys.exit(1)
        
        helper = AITranslationHelper()
        helper.import_ai_translations(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        main()