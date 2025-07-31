# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MP3Yap
Creates a single executable file for Windows
"""

import os
import sys
import static_ffmpeg
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the directory of this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Get FFmpeg binaries location
static_ffmpeg.add_paths()
ffmpeg_bin_dir = os.path.join(os.path.dirname(static_ffmpeg.__file__), 'bin', 'win32')

# Collect all data files
datas = [
    ('assets', 'assets'),  # Include icon files
]

# Collect FFmpeg binaries
binaries = [
    (os.path.join(ffmpeg_bin_dir, 'ffmpeg.exe'), '.'),
    (os.path.join(ffmpeg_bin_dir, 'ffprobe.exe'), '.'),
]

# Also include static_ffmpeg data files
try:
    static_ffmpeg_data = collect_data_files('static_ffmpeg')
    datas.extend(static_ffmpeg_data)
except:
    pass

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
    binaries=binaries,
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
    [],
    exclude_binaries=True,
    name='Youtube Mp3 İndir',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else 'assets/icon.png',
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Youtube Mp3 İndir',
)