#!/usr/bin/env python3
"""
Create a complete Windows package as a ZIP file
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_windows_package():
    """Create a ZIP package for Windows build"""
    
    print("📦 Creating Windows Package")
    print("=" * 40)
    
    # Package name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"MP3Yap_Windows_Build_{timestamp}"
    package_dir = package_name
    
    # Clean up if exists
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    if os.path.exists(f"{package_name}.zip"):
        os.remove(f"{package_name}.zip")
    
    # Create package directory
    os.makedirs(package_dir)
    
    # Files to include
    items = [
        # Source code
        ("mp3yap_gui.py", "src/mp3yap_gui.py"),
        ("mp3yap.py", "src/mp3yap.py"),
        ("ui/", "src/ui/"),
        ("core/", "src/core/"),
        ("database/", "src/database/"),
        ("utils/", "src/utils/"),
        
        # Resources
        ("assets/", "assets/"),
        
        # Build files
        ("requirements.txt", "requirements.txt"),
        ("requirements-dev.txt", "requirements-dev.txt"),
        ("mp3yap.spec", "mp3yap.spec"),
        ("version_info.txt", "version_info.txt"),
        ("mp3yap_installer.iss", "mp3yap_installer.iss"),
        ("LICENSE.txt", "LICENSE.txt"),
        ("README.md", "README.md"),
        
        # Scripts
        ("build.bat", "build.bat"),
        ("clean.bat", "clean.bat"),
        ("build_portable.bat", "build_portable.bat"),
        ("build_windows.py", "build_windows.py"),
    ]
    
    print("\n📋 Copying files...")
    for src, dst in items:
        full_dst = os.path.join(package_dir, dst)
        
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, full_dst, ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', '.DS_Store'))
                print(f"  ✓ {src} → {dst}")
            else:
                os.makedirs(os.path.dirname(full_dst), exist_ok=True)
                shutil.copy2(src, full_dst)
                print(f"  ✓ {src} → {dst}")
    
    # Create Windows README
    windows_readme = '''# MP3Yap Windows Build Package

## İçerik
- src/ - Kaynak kodlar
- assets/ - İkonlar ve görseller
- build.bat - Otomatik build scripti
- mp3yap_installer.iss - Inno Setup installer scripti

## Kurulum Adımları

### 1. Gereksinimler
- Windows 10/11
- Python 3.11 (3.13 ile uyumsuz!)
- Inno Setup 6 (installer için)

### 2. Python Kurulumu
1. https://python.org adresinden Python 3.11 indirin
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

### 3. Executable Oluşturma
1. Bu klasörde komut istemi açın
2. `build.bat` dosyasını çalıştırın
3. Executable `dist/MP3Yap.exe` konumunda oluşacak

### 4. Installer Oluşturma (Opsiyonel)
1. Inno Setup programını kurun
2. `mp3yap_installer.iss` dosyasını Inno Setup ile açın
3. Compile edin

## Notlar
- İlk build uzun sürebilir (bağımlılıklar indirilecek)
- Antivirüs uyarı verebilir (false positive)
- Sorun yaşarsanız `clean.bat` ile temizleyip tekrar deneyin
'''
    
    with open(os.path.join(package_dir, "README_WINDOWS.md"), "w", encoding="utf-8") as f:
        f.write(windows_readme)
    
    # Create simple build script
    simple_build = '''@echo off
echo MP3Yap Quick Build
echo ==================
echo.

REM Install requirements
pip install -r requirements.txt
pip install pyinstaller==6.3.0

REM Build
pyinstaller --clean mp3yap.spec

echo.
echo Build complete! Check dist/ folder.
pause
'''
    
    with open(os.path.join(package_dir, "quick_build.bat"), "w") as f:
        f.write(simple_build)
    
    print("\n🗜️ Creating ZIP archive...")
    
    # Create ZIP
    with zipfile.ZipFile(f"{package_name}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Clean up directory
    shutil.rmtree(package_dir)
    
    # Get file size
    size_mb = os.path.getsize(f"{package_name}.zip") / (1024 * 1024)
    
    print(f"\n✅ Package created successfully!")
    print(f"📦 File: {package_name}.zip")
    print(f"📏 Size: {size_mb:.2f} MB")
    print("\n🚀 Next steps:")
    print("1. Transfer the ZIP file to a Windows machine")
    print("2. Extract and follow README_WINDOWS.md")

if __name__ == "__main__":
    create_windows_package()