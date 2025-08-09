#!/usr/bin/env python3
"""Compile translation files using PyQt5's built-in functionality"""

import os
import sys
import subprocess
from pathlib import Path

def find_lrelease():
    """Try to find lrelease tool"""
    # Try common locations
    possible_paths = [
        # From PyQt5 tools
        "lrelease",
        "lrelease-qt5",
        "/usr/local/bin/lrelease",
        "/opt/homebrew/bin/lrelease",
        # Try to find it in Qt installation
        "/usr/local/opt/qt@5/bin/lrelease",
        "/usr/local/opt/qt/bin/lrelease",
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Found lrelease at: {path}")
                return path
        except:
            continue
    
    # Try to find it via which command
    try:
        result = subprocess.run(["which", "lrelease"], capture_output=True, text=True)
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"Found lrelease at: {path}")
            return path
    except:
        pass
    
    return None

def compile_with_lrelease(lrelease_path):
    """Compile .ts files to .qm using lrelease"""
    translations_dir = Path(__file__).parent / "translations"
    
    for ts_file in translations_dir.glob("*.ts"):
        qm_file = ts_file.with_suffix(".qm")
        
        try:
            result = subprocess.run(
                [lrelease_path, str(ts_file), "-qm", str(qm_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Compiled {ts_file.name} -> {qm_file.name}")
            else:
                print(f"✗ Failed to compile {ts_file.name}: {result.stderr}")
        except Exception as e:
            print(f"✗ Error compiling {ts_file.name}: {e}")

def compile_with_pylupdate5():
    """Try to use pylupdate5/pyrcc5 tools"""
    try:
        # Try to import PyQt5 tools
        from PyQt5.pylupdate_main import main as pylupdate_main
        print("Found PyQt5 lupdate tools")
        
        # This would need more complex setup
        return False
    except:
        return False

def main():
    """Main compilation function"""
    print("Attempting to compile translation files...")
    
    # First try to find lrelease
    lrelease = find_lrelease()
    if lrelease:
        compile_with_lrelease(lrelease)
        return
    
    # Try PyQt5 tools
    if compile_with_pylupdate5():
        return
    
    print("\n⚠️  Could not find Qt translation tools.")
    print("\n❌ Could not compile translations.")
    print("Please install Qt5 tools manually:")
    print("  macOS: brew install qt@5")
    print("  Linux: apt-get install qttools5-dev-tools")
    print("  Windows: Install Qt5 from https://www.qt.io/")

if __name__ == "__main__":
    main()