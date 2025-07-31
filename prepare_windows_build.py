#!/usr/bin/env python3
"""
Prepare files for Windows build
This script prepares all necessary files for building on Windows
"""

import os
import shutil
import json

def prepare_build_files():
    """Prepare all files needed for Windows build"""
    
    print("🚀 Preparing Windows Build Files")
    print("=" * 40)
    
    # Create windows_build directory
    build_dir = "windows_build"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Files and directories to copy
    items_to_copy = [
        # Python files
        "mp3yap_gui.py",
        "mp3yap.py",
        "ui/",
        "core/",
        "database/",
        "utils/",
        
        # Resources
        "assets/",
        
        # Requirements
        "requirements.txt",
        "requirements-dev.txt",
        
        # Build files
        "mp3yap.spec",
        "version_info.txt",
        "build_windows.py",
        "LICENSE.txt",
        "README.md",
        
        # Batch files
        "build.bat",
        "clean.bat",
        
        # Installer script
        "mp3yap_installer.iss"
    ]
    
    print("\n📁 Copying files...")
    for item in items_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                dest = os.path.join(build_dir, item)
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                print(f"  ✓ Copied directory: {item}")
            else:
                dest = os.path.join(build_dir, item)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(item, dest)
                print(f"  ✓ Copied file: {item}")
        else:
            print(f"  ⚠ Skipped (not found): {item}")
    
    # Create build info
    build_info = {
        "version": "2.1.0",
        "build_date": "2025-01-31",
        "python_version": "3.11",
        "notes": "Build on Windows with Python 3.11 for best results"
    }
    
    with open(os.path.join(build_dir, "build_info.json"), "w") as f:
        json.dump(build_info, f, indent=2)
    
    print("\n✅ Build files prepared!")
    print(f"\n📦 Output directory: {build_dir}/")
    print("\nNext steps:")
    print("1. Copy the 'windows_build' folder to a Windows machine")
    print("2. Install Python 3.11 on Windows")
    print("3. Run 'build.bat' in the windows_build folder")
    print("4. The executable will be in 'dist/MP3Yap.exe'")

def create_portable_batch():
    """Create a portable batch file for Windows"""
    
    portable_bat = '''@echo off
echo MP3Yap Portable Build Script
echo ============================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11 from python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Build executable
echo.
echo Building executable...
python -m PyInstaller --clean mp3yap.spec

echo.
if exist dist\\MP3Yap.exe (
    echo SUCCESS: Executable created at dist\\MP3Yap.exe
) else (
    echo ERROR: Build failed!
)

echo.
pause
'''
    
    with open("build_portable.bat", "w") as f:
        f.write(portable_bat)
    
    print("✓ Created build_portable.bat")

if __name__ == "__main__":
    prepare_build_files()
    create_portable_batch()