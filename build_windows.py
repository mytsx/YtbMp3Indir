#!/usr/bin/env python3
"""
Build script for creating Windows executable and installer
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_ico_file():
    """Create ICO file from PNG if it doesn't exist"""
    if not os.path.exists('assets/icon.ico'):
        try:
            from PIL import Image
            
            # Open PNG icon
            img = Image.open('assets/icon.png')
            
            # Create ICO with multiple sizes
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Save as ICO
            img.save('assets/icon.ico', format='ICO', sizes=icon_sizes)
            print("✓ Created icon.ico from icon.png")
        except Exception as e:
            print(f"⚠ Could not create ICO file: {e}")
            print("  Using PNG icon instead")

def build_exe():
    """Build executable using PyInstaller"""
    print("\n🔨 Building executable with PyInstaller...")
    
    # Clean previous builds
    for path in ['build', 'dist']:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # Create ICO file
    create_ico_file()
    
    # Run PyInstaller
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'mp3yap.spec']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Executable built successfully!")
        print(f"  Location: dist/MP3Yap.exe")
        return True
    else:
        print("✗ Build failed!")
        print("Error:", result.stderr)
        return False

def create_installer():
    """Create Inno Setup installer script"""
    print("\n📦 Creating installer configuration...")
    
    # Check if executable exists
    if not os.path.exists('dist/MP3Yap.exe'):
        print("✗ Executable not found! Build it first.")
        return False
    
    # Create Inno Setup script
    with open('mp3yap_installer.iss', 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print("✓ Installer script created: mp3yap_installer.iss")
    print("\nTo create the installer:")
    print("1. Install Inno Setup from: https://jrsoftware.org/isdl.php")
    print("2. Open mp3yap_installer.iss in Inno Setup")
    print("3. Click 'Build' -> 'Compile'")
    print("\nOr run from command line:")
    print('  "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" mp3yap_installer.iss')
    
    return True

# Inno Setup script template
installer_script = '''#define MyAppName "YouTube MP3 İndirici"
#define MyAppVersion "2.1"
#define MyAppPublisher "MP3Yap"
#define MyAppURL "https://github.com/yourusername/mp3yap"
#define MyAppExeName "MP3Yap.exe"

[Setup]
AppId={{E8F9C5A2-4B7D-4F3E-9C1A-2D3E4F5A6B7C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
OutputDir=installer_output
OutputBaseFilename=MP3Yap_Setup_{#MyAppVersion}
SetupIconFile=assets\\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\\{#MyAppExeName}

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\MP3Yap.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
'''

def create_batch_files():
    """Create batch files for easy building"""
    
    # Build batch file
    with open('build.bat', 'w') as f:
        f.write('''@echo off
echo Building MP3Yap for Windows...
echo.

REM Activate virtual environment if exists
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Run build script
echo.
echo Running build script...
python build_windows.py

echo.
echo Build complete!
pause
''')
    
    # Clean batch file
    with open('clean.bat', 'w') as f:
        f.write('''@echo off
echo Cleaning build artifacts...

REM Remove build directories
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Remove spec file artifacts
if exist *.spec del *.spec

echo.
echo Clean complete!
pause
''')
    
    print("\n✓ Created batch files:")
    print("  - build.bat: Build the application")
    print("  - clean.bat: Clean build artifacts")

def main():
    """Main build process"""
    print("🚀 MP3Yap Windows Build Script")
    print("=" * 40)
    
    # Check if we're on Windows
    if sys.platform != 'win32':
        print("⚠ Warning: This script is designed for Windows.")
        print("  Running in preparation mode for cross-platform build.")
    
    # Create batch files
    create_batch_files()
    
    # Build executable
    if build_exe():
        # Create installer script
        create_installer()
        
        print("\n✅ Build process complete!")
        print("\nNext steps:")
        print("1. Transfer the project to a Windows machine")
        print("2. Run 'build.bat' to build the executable")
        print("3. Use Inno Setup to create the installer")
    else:
        print("\n❌ Build failed!")

if __name__ == "__main__":
    main()