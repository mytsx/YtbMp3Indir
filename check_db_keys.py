import sqlite3
import os

db_path = 'data/translations.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

try:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        print("--- Translation Keys ---")
        cursor.execute("SELECT key_text FROM translation_keys")
        keys = cursor.fetchall()
        for key in keys:
            print(key[0])

        print("\n--- Translations (TR) ---")
        cursor.execute("""
            SELECT k.key_text, t.translated_text
            FROM translation_keys k
            JOIN translations t ON k.key_id = t.key_id
            WHERE t.lang_code = 'tr'
        """)
        translations = cursor.fetchall()
        for key, text in translations:
            print(f"{key}: {text}")
except sqlite3.Error as e:
    print(f"Database error: {e}")
except Exception:
    print("An unexpected error occurred:")
    import traceback
    traceback.print_exc()
