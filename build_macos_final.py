#!/usr/bin/env python3
"""
macOS için MP3Yap build ve sign scripti
"""
import os
import sys
import subprocess
import shutil

# Configuration
DEVELOPER_ID = "Developer ID Application: Mehmet Yerli (VTVG4G3NFH)"
BUNDLE_ID = "com.mp3yap.app"
NOTARIZE_PROFILE = "MP3YAP_NOTARIZE"
APP_VERSION = "2.1.1"

def run_command(cmd, description):
    """Run command and show output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """Main build process"""
    print("🎯 MP3Yap macOS Build Script")
    print("="*60)
    
    # 1. Clean old builds
    print("\n📦 Cleaning old builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  - {folder}/ cleaned")
    
    # 2. Create PyInstaller spec
    print("\n📄 Creating spec file...")
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
import sys

spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['mp3yap_gui_macos.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('ui', 'ui'),
        ('core', 'core'),
        ('database', 'database'),
        ('utils', 'utils'),
        ('assets/ffmpeg/darwin', 'static_ffmpeg/bin/darwin'),
    ],
    hiddenimports=[
        'PyQt5.sip',
        'yt_dlp',
        'static_ffmpeg',
        'certifi',
        'requests',
        'urllib3',
        'sqlite3',
        'subprocess',
        'platform',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MP3Yap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MP3Yap',
)

app = BUNDLE(
    coll,
    name='MP3Yap.app',
    icon='assets/icon.icns',
    bundle_identifier='{BUNDLE_ID}',
    info_plist={{
        'CFBundleDisplayName': 'YouTube MP3 İndirici',
        'CFBundleExecutable': 'MP3Yap',
        'CFBundleIdentifier': '{BUNDLE_ID}',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleName': 'MP3Yap',
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '{APP_VERSION}',
        'CFBundleVersion': '{APP_VERSION}',
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'NSRequiresAquaSystemAppearance': False,
        'NSAppTransportSecurity': {{
            'NSAllowsArbitraryLoads': True
        }},
        'LSApplicationCategoryType': 'public.app-category.music',
        'LSEnvironment': {{
            'QT_MAC_WANTS_LAYER': '1',
            'PYQT_DISABLE_MAIN_THREAD_CHECKER': '1'
        }}
    }},
)
'''
    
    with open('mp3yap_macos.spec', 'w') as f:
        f.write(spec_content)
    
    # 3. Build with PyInstaller
    if not run_command(
        'python -m PyInstaller --clean mp3yap_macos.spec',
        'Building with PyInstaller'
    ):
        print("❌ Build failed!")
        return
    
    # 4. Sign the app
    if not run_command(
        f'codesign --deep --force --verbose --sign "{DEVELOPER_ID}" dist/MP3Yap.app',
        'Signing the app'
    ):
        print("❌ Signing failed!")
        return
    
    # 5. Verify signature
    run_command(
        'codesign --verify --deep --strict --verbose=2 dist/MP3Yap.app',
        'Verifying signature'
    )
    
    # 6. Test the app
    print("\n🧪 Testing the app...")
    print("Opening the app for 5 seconds...")
    subprocess.run("open dist/MP3Yap.app", shell=True)
    import time
    time.sleep(5)
    
    # Check if running
    result = subprocess.run("ps aux | grep -i mp3yap | grep -v grep", 
                          shell=True, capture_output=True, text=True)
    if result.stdout:
        print("✅ App is running!")
    else:
        response = input("\n⚠️  App doesn't appear to be running. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Build cancelled")
            return
    
    # 7. Create DMG
    dmg_name = f'MP3Yap-{APP_VERSION}.dmg'
    if os.path.exists(dmg_name):
        os.remove(dmg_name)
    
    if not run_command(
        f"hdiutil create -volname 'MP3Yap' -srcfolder dist/MP3Yap.app "
        f"-ov -format UDZO '{dmg_name}'",
        'Creating DMG'
    ):
        print("❌ DMG creation failed!")
        return
    
    # 7. Sign DMG
    if not run_command(
        f'codesign --sign "{DEVELOPER_ID}" --timestamp "{dmg_name}"',
        'Signing DMG'
    ):
        print("❌ DMG signing failed!")
        return
    
    # 8. Notarize
    print("\n🔔 Ready to submit for notarization...")
    response = input("Submit for notarization? This may take 5-30 minutes. (y/n): ")
    if response.lower() != 'y':
        print("✅ Build complete without notarization!")
        print(f"   DMG ready: {dmg_name}")
        return
    
    print("\n🔔 Submitting for notarization...")
    if not run_command(
        f"xcrun notarytool submit '{dmg_name}' --keychain-profile '{NOTARIZE_PROFILE}' --wait",
        'Notarizing DMG'
    ):
        print("❌ Notarization failed!")
        return
    
    # 9. Staple
    run_command(
        f"xcrun stapler staple '{dmg_name}'",
        'Stapling notarization ticket'
    )
    
    print(f"\n✅ Build complete! DMG ready: {dmg_name}")
    print("\n🎉 Your app is:")
    print("   - Signed with Developer ID")
    print("   - Notarized by Apple")
    print("   - Ready for distribution")

if __name__ == "__main__":
    main()