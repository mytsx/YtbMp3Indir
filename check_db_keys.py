import sqlite3
import os

db_path = 'data/translations.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Translation Keys ---")
try:
    cursor.execute("SELECT key_text FROM translation_keys")
    keys = cursor.fetchall()
    for key in keys:
        print(key[0])
except Exception as e:
    print(f"Error reading keys: {e}")

print("\n--- Translations (TR) ---")
try:
    cursor.execute("""
        SELECT k.key_text, t.translated_text 
        FROM translation_keys k 
        JOIN translations t ON k.key_id = t.key_id 
        WHERE t.lang_code = 'tr'
    """)
    translations = cursor.fetchall()
    for key, text in translations:
        print(f"{key}: {text}")
except Exception as e:
    print(f"Error reading translations: {e}")

conn.close()
