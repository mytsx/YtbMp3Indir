#!/usr/bin/env python3
"""
Automatically replace hardcoded strings with translation keys in UI files.
"""

import os
import sys
import json
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

MAPPING_FILE = Path(__file__).parent / 'translation_key_mapping_comprehensive.json'

# Files to process
UI_FILES = [
    project_root / 'ui' / 'main_window.py',
    project_root / 'ui' / 'queue_widget.py',
    project_root / 'ui' / 'history_widget.py',
    project_root / 'ui' / 'settings_dialog.py',
    project_root / 'ui' / 'converter_widget.py',
    project_root / 'ui' / 'splash_screen.py',
    project_root / 'ui' / 'preloader_widget.py',
]


def load_mapping():
    """Load the comprehensive key mapping"""
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten the mapping to create old_string -> new_key mapping
    flat_mapping = {}
    for category, mappings in data['mapping'].items():
        for old_string, new_key in mappings.items():
            flat_mapping[old_string] = new_key

    return flat_mapping


def replace_in_file(file_path, mapping):
    """Replace hardcoded strings in a single file"""
    print(f"\n📝 Processing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements = 0

    # Sort by length (longest first) to avoid partial replacements
    sorted_mapping = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)

    for old_string, new_key in sorted_mapping:
        # Escape special regex characters in old_string
        escaped_old = re.escape(old_string)

        # Pattern to match: translation_manager.tr('old_string') or translation_manager.tr("old_string")
        pattern = r"translation_manager\.tr\(['\"]" + escaped_old + r"['\"]\)"
        replacement = f"translation_manager.tr(\"{new_key}\")"

        if re.search(pattern, content):
            content, count = re.subn(pattern, replacement, content)
            if count > 0:
                replacements += count
                print(f"  ✓ Replaced '{old_string[:50]}...' → '{new_key}' ({count}x)")

    # Save if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 Saved {replacements} replacements")
        return replacements
    else:
        print(f"  ⏭️  No changes needed")
        return 0


def main():
    """Main replacement function"""
    print("=" * 80)
    print("AUTOMATIC HARDCODED STRING REPLACEMENT")
    print("=" * 80)

    # Load mapping
    print(f"\n📖 Loading mapping from: {MAPPING_FILE}")
    mapping = load_mapping()
    print(f"✓ Loaded {len(mapping)} string mappings")

    # Process each file
    total_replacements = 0
    for file_path in UI_FILES:
        if not file_path.exists():
            print(f"\n⚠️  File not found: {file_path}")
            continue

        replacements = replace_in_file(file_path, mapping)
        total_replacements += replacements

    print("\n" + "=" * 80)
    print(f"✅ COMPLETED! Total replacements: {total_replacements}")
    print("=" * 80)


if __name__ == '__main__':
    main()
