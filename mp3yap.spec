# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MP3Yap
Creates a single executable file for Windows
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the directory of this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect all data files
datas = [
    ('assets', 'assets'),  # Include icon files
    ('static_ffmpeg', 'static_ffmpeg'),  # Include FFmpeg if needed
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'yt_dlp',
    'yt_dlp.extractor',
    'yt_dlp.downloader',
    'yt_dlp.postprocessor',
    'static_ffmpeg',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
]

# Collect all yt-dlp submodules
hiddenimports.extend(collect_submodules('yt_dlp'))

a = Analysis(
    ['mp3yap_gui.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MP3Yap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else 'assets/icon.png',
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)