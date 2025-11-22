"""Script to add missing settings-related translation keys to the database."""

from database.translation_db import TranslationDatabase


def add_settings_keys():
    """Add missing settings keys to translation database."""
    db = TranslationDatabase()

    new_keys = [
        {
            'full_key': 'dialogs.messages.language_change_error',
            'translations': {
                'tr': 'Dil değiştirilemedi. Lütfen tekrar deneyin.',
                'en': 'Could not change language. Please try again.',
                'de': 'Sprache konnte nicht geändert werden. Bitte versuchen Sie es erneut.',
                'es': 'No se pudo cambiar el idioma. Por favor inténtelo de nuevo.',
                'fr': 'Impossible de changer la langue. Veuillez réessayer.'
            }
        },
        {
            'full_key': 'settings.suffixes.url',
            'translations': {
                'tr': ' URL',
                'en': ' URL',
                'de': ' URL',
                'es': ' URL',
                'fr': ' URL'
            }
        },
        {
            'full_key': 'settings.suffixes.kbps',
            'translations': {
                'tr': ' kbps',
                'en': ' kbps',
                'de': ' kbps',
                'es': ' kbps',
                'fr': ' kbps'
            }
        }
    ]

    print("Adding missing settings keys...")

    for item in new_keys:
        full_key = item['full_key']
        translations = item['translations']

        # Split scope and key_text
        if '.' in full_key:
            scope, key_text = full_key.rsplit('.', 1)
        else:
            scope = ''
            key_text = full_key

        print(f"Processing {full_key} (Scope: {scope}, Key: {key_text})")

        # Add for each language
        for lang_code, text in translations.items():
            try:
                # add_translation handles key creation if not exists
                # Note: add_translation takes (key, lang_code, text, scope)
                # It uses key_text for lookup.
                db.add_translation(key_text, lang_code, text, scope or '')
                print(f"  Added {lang_code}: {text}")
            except (ValueError, KeyError, OSError) as e:
                print(f"  Error adding {lang_code}: {e}")

    print("Done.")

if __name__ == "__main__":
    add_settings_keys()
