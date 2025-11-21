#!/usr/bin/env python3
"""
Unified translation management tool for MP3 Yap
Handles database-based translations and Qt .qm file compilation
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def find_lrelease():
    """Try to find lrelease tool for compiling Qt translations"""
    possible_paths = [
        # Common locations
        "lrelease",
        "lrelease-qt5",
        "/usr/local/bin/lrelease",
        "/opt/homebrew/bin/lrelease",
        # Qt installation paths
        "/usr/local/opt/qt@5/bin/lrelease",
        "/usr/local/opt/qt/bin/lrelease",
        "/opt/homebrew/opt/qt@5/bin/lrelease",
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                return path
        except:
            continue
    
    # Try to find via which command
    try:
        result = subprocess.run(["which", "lrelease"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None


def compile_qt_translations():
    """Compile .ts files to .qm format for Qt"""
    translations_dir = Path(__file__).parent / "translations"
    
    if not translations_dir.exists():
        print(f"Creating translations directory: {translations_dir}")
        translations_dir.mkdir(exist_ok=True)
    
    # Find lrelease tool
    lrelease = find_lrelease()
    
    if not lrelease:
        print("Warning: lrelease not found. Creating placeholder .qm files...")
        # Create minimal placeholder .qm files that Qt will accept
        for ts_file in translations_dir.glob("*.ts"):
            qm_file = ts_file.with_suffix(".qm")
            with open(qm_file, 'wb') as f:
                # Write minimal QM file header
                f.write(bytes.fromhex('3CB86418CAEF9C95CD211CBF60A1BDDD'))
                # Write empty content section
                f.write(bytes.fromhex('00000020'))  # Offset to data
                f.write(bytes.fromhex('00000000'))  # No messages
            print(f"Created placeholder: {qm_file.name}")
    else:
        # Use lrelease to compile
        print(f"Using lrelease at: {lrelease}")
        for ts_file in translations_dir.glob("*.ts"):
            qm_file = ts_file.with_suffix(".qm")
            cmd = [lrelease, str(ts_file), "-qm", str(qm_file)]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Compiled: {ts_file.name} -> {qm_file.name}")
                else:
                    print(f"Error compiling {ts_file.name}: {result.stderr}")
            except Exception as e:
                print(f"Failed to compile {ts_file.name}: {e}")


def update_database_translations():
    """Update translations in the SQLite database"""
    try:
        from database.translation_db import translation_db
        
        # Ensure database is initialized
        translation_db._init_database()
        
        # Get current translations from database
        print("\nDatabase translation system is active")
        print(f"Database path: {translation_db.db_path}")
        
        # Count translations
        import sqlite3
        with sqlite3.connect(translation_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM translation_keys")
            key_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM translations")
            trans_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT lang_code) FROM translations")
            lang_count = cursor.fetchone()[0]
        
        print(f"Translation keys: {key_count}")
        print(f"Translations: {trans_count}")
        print(f"Languages: {lang_count}")
        
    except ImportError:
        print("Database translation system not available")
    except Exception as e:
        print(f"Error accessing translation database: {e}")


def list_translations():
    """List all available translations"""
    translations_dir = Path(__file__).parent / "translations"
    
    print("\nAvailable translation files:")
    print("-" * 40)
    
    # List .ts files
    ts_files = list(translations_dir.glob("*.ts"))
    if ts_files:
        print("\nSource files (.ts):")
        for ts_file in sorted(ts_files):
            print(f"  - {ts_file.name}")
    
    # List .qm files
    qm_files = list(translations_dir.glob("*.qm"))
    if qm_files:
        print("\nCompiled files (.qm):")
        for qm_file in sorted(qm_files):
            size = qm_file.stat().st_size
            print(f"  - {qm_file.name} ({size} bytes)")
    
    if not ts_files and not qm_files:
        print("  No translation files found")


def clean_translations():
    """Remove compiled .qm files"""
    translations_dir = Path(__file__).parent / "translations"
    
    qm_files = list(translations_dir.glob("*.qm"))
    if qm_files:
        print(f"\nRemoving {len(qm_files)} compiled translation files...")
        for qm_file in qm_files:
            qm_file.unlink()
            print(f"  Removed: {qm_file.name}")
    else:
        print("\nNo compiled translation files to remove")


def main():
    parser = argparse.ArgumentParser(
        description="MP3 Yap Translation Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s compile    # Compile all translations
  %(prog)s list       # List available translations
  %(prog)s clean      # Remove compiled files
  %(prog)s update-db  # Update database translations
  %(prog)s all        # Compile and update everything
        """
    )
    
    parser.add_argument(
        'action',
        choices=['compile', 'list', 'clean', 'update-db', 'all'],
        help='Action to perform'
    )
    
    args = parser.parse_args()
    
    if args.action == 'compile':
        compile_qt_translations()
    elif args.action == 'list':
        list_translations()
    elif args.action == 'clean':
        clean_translations()
    elif args.action == 'update-db':
        update_database_translations()
    elif args.action == 'all':
        compile_qt_translations()
        update_database_translations()
        list_translations()


if __name__ == "__main__":
    main()