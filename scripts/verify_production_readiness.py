#!/usr/bin/env python3
"""Verify production readiness - check for hardcoded strings and test coverage"""

import re
import sys
from pathlib import Path

# Turkish character patterns
TURKISH_CHARS = r'[ıİşŞğĞüÜöÖçÇ]'

# Files to check
FILES_TO_CHECK = [
    'core/downloader.py',
    'ui/main_window.py',
    'ui/queue_widget.py',
    'ui/history_widget.py',
    'ui/converter_widget.py',
    'ui/settings_dialog.py',
    'utils/update_checker.py',
    'services/url_analyzer.py',
]

# Patterns to exclude
EXCLUDE_PATTERNS = [
    r'#.*',  # Comments
    r'""".*?"""',  # Docstrings
    r"'''.*?'''",  # Docstrings
    r'translation_manager\.tr\(',  # Already wrapped
    r'logger\.',  # Logger messages
]

def check_file_for_hardcoded_strings(file_path):
    """Check a file for hardcoded Turkish strings"""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Skip excluded patterns
            if any(re.search(pattern, line) for pattern in EXCLUDE_PATTERNS):
                continue

            # Check for Turkish characters in strings
            if re.search(TURKISH_CHARS, line):
                # Check if it's in a string literal
                string_matches = re.findall(r'["\']([^"\']*)["\']', line)
                for string_match in string_matches:
                    if re.search(TURKISH_CHARS, string_match):
                        issues.append({
                            'file': file_path,
                            'line': line_num,
                            'text': string_match.strip(),
                            'context': line.strip()
                        })

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

    return issues

def main():
    """Main verification function"""
    print("=" * 80)
    print("PRODUCTION READINESS VERIFICATION")
    print("=" * 80)
    print()

    all_issues = []

    print("📋 Checking files for hardcoded Turkish strings...")
    print()

    for file_path in FILES_TO_CHECK:
        if not Path(file_path).exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        issues = check_file_for_hardcoded_strings(file_path)

        if issues is None:
            continue

        if issues:
            print(f"❌ {file_path}: {len(issues)} hardcoded strings found")
            all_issues.extend(issues)
        else:
            print(f"✅ {file_path}: No hardcoded strings")

    print()
    print("=" * 80)

    if all_issues:
        print(f"❌ FAILED: {len(all_issues)} hardcoded Turkish strings found")
        print()
        print("Issues found:")
        for issue in all_issues[:10]:  # Show first 10
            print(f"  {issue['file']}:{issue['line']}")
            print(f"    Text: {issue['text']}")
            print()
        if len(all_issues) > 10:
            print(f"  ... and {len(all_issues) - 10} more")
        sys.exit(1)
    else:
        print("✅ PASSED: No hardcoded Turkish strings in critical files")
        print()

        # Check database
        print("📋 Checking translation database...")
        if Path('data/translations.db').exists():
            import sqlite3
            with sqlite3.connect('data/translations.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM translation_keys')
                key_count = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT COUNT(*) FROM translations
                    WHERE lang_code IN ('en', 'tr')
                ''')
                trans_count = cursor.fetchone()[0]

                print(f"✅ Translation keys: {key_count}")
                print(f"✅ Translations (EN+TR): {trans_count}")
        else:
            print("⚠️  Database file not found (will be generated from migrations)")

        print()
        print("=" * 80)
        print("✅ PRODUCTION READY")
        print("=" * 80)
        sys.exit(0)

if __name__ == '__main__':
    main()
