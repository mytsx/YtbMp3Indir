#!/usr/bin/env python3
"""Find missing translation keys by comparing code usage with database"""

import os
import re
import sqlite3

# Get all translation keys used in code
def extract_keys_from_code():
    keys = set()
    pattern = re.compile(r'translation_manager\.tr\(["\']([^"\']+)["\']\)')

    for root, dirs, files in os.walk('ui'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    keys.update(matches)

    return keys

# Get all keys from database
def get_db_keys():
    db_path = 'data/translations.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key_text FROM translation_keys")
    keys = {row[0] for row in cursor.fetchall()}
    conn.close()
    return keys

# Main analysis
code_keys = extract_keys_from_code()
db_keys = get_db_keys()

print("=" * 80)
print("TRANSLATION KEY ANALYSIS")
print("=" * 80)

# Filter to only hierarchical keys (contains dots)
hierarchical_code_keys = {k for k in code_keys if '.' in k}
hierarchical_db_keys = {k for k in db_keys if '.' in k}

print(f"\nTotal keys in code: {len(code_keys)}")
print(f"Hierarchical keys in code: {len(hierarchical_code_keys)}")
print(f"Total keys in database: {len(db_keys)}")
print(f"Hierarchical keys in database: {len(hierarchical_db_keys)}")

# Missing in database
missing_in_db = code_keys - db_keys
if missing_in_db:
    print(f"\n❌ MISSING IN DATABASE ({len(missing_in_db)}):")
    for key in sorted(missing_in_db):
        print(f"  - {key}")
else:
    print("\n✅ All code keys exist in database!")

# Extra in database (not used in code)
extra_in_db = db_keys - code_keys
if extra_in_db:
    hierarchical_extra = {k for k in extra_in_db if '.' in k}
    print(f"\n⚠️  UNUSED IN CODE ({len(extra_in_db)} total, {len(hierarchical_extra)} hierarchical):")
    for key in sorted(hierarchical_extra)[:30]:  # Show first 30
        print(f"  - {key}")
    if len(hierarchical_extra) > 30:
        print(f"  ... and {len(hierarchical_extra) - 30} more")

print("\n" + "=" * 80)
