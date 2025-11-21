#!/usr/bin/env python3
"""
Update all translation calls to use abstract keys
"""

import json
import re
from pathlib import Path

def load_mappings():
    """Load the translation key mappings"""
    with open('translation_keys_mapping.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['mappings']

def update_file(file_path, mappings):
    """Update a single file to use abstract keys"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Find all translation_manager.tr() calls
    pattern = r'translation_manager\.tr\("([^"]+)"\)'
    
    def replace_func(match):
        old_key = match.group(1)
        if old_key in mappings:
            new_key = mappings[old_key]
            changes_made.append(f"  {old_key} -> {new_key}")
            return f'translation_manager.tr("{new_key}")'
        return match.group(0)
    
    content = re.sub(pattern, replace_func, content)
    
    # Also handle tr() calls with escaped quotes
    pattern2 = r'translation_manager\.tr\(\'([^\']+)\'\)'
    
    def replace_func2(match):
        old_key = match.group(1)
        if old_key in mappings:
            new_key = mappings[old_key]
            changes_made.append(f"  {old_key} -> {new_key}")
            return f'translation_manager.tr("{new_key}")'
        return match.group(0)
    
    content = re.sub(pattern2, replace_func2, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {file_path.name}:")
        for change in changes_made:
            print(change)
        return True
    return False

def main():
    """Update all Python files to use abstract keys"""
    mappings = load_mappings()
    
    # Files to update
    files_to_update = [
        'ui/main_window.py',
        'ui/history_widget.py',
        'ui/queue_widget.py',
        'ui/converter_widget.py',
        'ui/settings_dialog.py',
    ]
    
    total_updated = 0
    for file_path_str in files_to_update:
        file_path = Path(file_path_str)
        if file_path.exists():
            if update_file(file_path, mappings):
                total_updated += 1
        else:
            print(f"✗ File not found: {file_path}")
    
    print(f"\nTotal files updated: {total_updated}")

if __name__ == "__main__":
    main()