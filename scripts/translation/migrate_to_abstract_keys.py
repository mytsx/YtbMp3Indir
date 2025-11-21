#!/usr/bin/env python3
"""
Migration script to convert Turkish text keys to abstract keys
"""

import json
import sqlite3
import os
from pathlib import Path

def migrate_translations():
    """Migrate from Turkish text keys to abstract keys"""
    
    # Load mapping
    with open('translation_keys_mapping.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        mappings = data['mappings']
    
    # Connect to database - use the same path as translation_db.py
    from database.translation_db import translation_db
    db_path = Path(translation_db.db_path)
    
    print(f"Using database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting migration to abstract keys...")
    print(f"Found {len(mappings)} keys to migrate")
    
    # Create backup table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translation_keys_backup AS 
        SELECT * FROM translation_keys
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations_backup AS 
        SELECT * FROM translations
    ''')
    print("Backup tables created")
    
    # Get all current keys
    cursor.execute('''
        SELECT key_id, key_text FROM translation_keys
    ''')
    current_keys = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Update each key
    migrated = 0
    skipped = 0
    
    for old_key, new_key in mappings.items():
        if old_key in current_keys:
            key_id = current_keys[old_key]
            
            # Update the key text to abstract key
            cursor.execute('''
                UPDATE translation_keys 
                SET key_text = ?, 
                    default_text = ?,
                    description = ?
                WHERE key_id = ?
            ''', (new_key, old_key, f"Migrated from: {old_key}", key_id))
            
            migrated += 1
            print(f"✓ Migrated: {old_key} -> {new_key}")
        else:
            # Create new key if doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO translation_keys (key_text, default_text, description)
                VALUES (?, ?, ?)
            ''', (new_key, old_key, f"Added during migration"))
            
            # Get the new key_id
            cursor.execute('SELECT key_id FROM translation_keys WHERE key_text = ?', (new_key,))
            result = cursor.fetchone()
            if result:
                new_key_id = result[0]
                
                # Add Turkish translation
                cursor.execute('''
                    INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text)
                    VALUES (?, 'tr', ?)
                ''', (new_key_id, old_key))
                
                # Add English translation (use old_key as fallback)
                cursor.execute('''
                    INSERT OR REPLACE INTO translations (key_id, lang_code, translated_text)
                    VALUES (?, 'en', ?)
                ''', (new_key_id, old_key))
                
                migrated += 1
                print(f"✓ Created: {old_key} -> {new_key}")
            else:
                skipped += 1
                print(f"✗ Skipped: {old_key}")
    
    # Commit changes
    conn.commit()
    
    print(f"\nMigration completed!")
    print(f"  Migrated: {migrated} keys")
    print(f"  Skipped: {skipped} keys")
    print(f"  Backup tables created: translation_keys_backup, translations_backup")
    
    # Verify migration
    cursor.execute('SELECT COUNT(*) FROM translation_keys WHERE key_text LIKE "%.%"')
    abstract_count = cursor.fetchone()[0]
    print(f"  Abstract keys in database: {abstract_count}")
    
    conn.close()

if __name__ == "__main__":
    migrate_translations()