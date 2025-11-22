#!/usr/bin/env python3
"""
Fix incorrect scopes in translation_keys table

Scope should be extracted from key_text up to the last dot.
For example: "main.buttons.download" -> scope should be "main.buttons", not "main"
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'translations.db'

def extract_correct_scope(key_text):
    """Extract correct scope from key_text (everything before last dot)"""
    if '.' not in key_text:
        return None
    parts = key_text.rsplit('.', 1)
    return parts[0] if len(parts) == 2 else None

def fix_scopes():
    """Fix all incorrect scopes in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all keys with their current scopes
        cursor.execute("SELECT key_id, scope, key_text FROM translation_keys WHERE key_text LIKE '%.%'")
        keys = cursor.fetchall()

        fixed_count = 0
        for key_id, current_scope, key_text in keys:
            correct_scope = extract_correct_scope(key_text)

            if correct_scope and correct_scope != current_scope:
                print(f"Fixing: {key_text}")
                print(f"  Current scope: {current_scope}")
                print(f"  Correct scope: {correct_scope}")

                cursor.execute(
                    "UPDATE translation_keys SET scope = ? WHERE key_id = ?",
                    (correct_scope, key_id)
                )
                fixed_count += 1

        conn.commit()
        print(f"\n✓ Fixed {fixed_count} incorrect scopes")

        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if fix_scopes():
        print("\n✓ Successfully fixed translation scopes")
    else:
        print("\n✗ Failed to fix scopes")
