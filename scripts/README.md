# Icon Processing Scripts

This directory contains scripts for processing application icons.

## Scripts

### 1. `process_icon_transparent.py`
Removes white background from an image and makes it transparent.

**Usage:**
```bash
python scripts/process_icon_transparent.py [image_path]
```

**Default:** Uses `image.png` if no path provided.

### 2. `crop_icon.py`
Crops an icon to remove extra transparent space around it.

**Usage:**
```bash
python scripts/crop_icon.py [icon_path]
```

**Default:** Uses `assets/icon.png` if no path provided.

### 3. `create_icon_from_scratch.py`
Creates a new MP3 downloader icon from scratch (red circle with music note and download arrow).

**Usage:**
```bash
python scripts/create_icon_from_scratch.py
```

### 4. `process_all_icons.py`
Runs the complete icon processing pipeline:
1. Removes white background
2. Crops extra space
3. Creates all required sizes

**Usage:**
```bash
python scripts/process_all_icons.py [image_path]
```

**Default:** Uses `image.png` if no path provided.

## Requirements

- Python 3.x
- Pillow (PIL): `pip install Pillow`
- NumPy: `pip install numpy` (only for transparent processing)

## Output

All processed icons are saved in the `assets/` directory with the following files:
- `icon.png` - Main icon
- `icon_16x16.png` - 16x16 version
- `icon_32x32.png` - 32x32 version
- `icon_48x48.png` - 48x48 version
- `icon_64x64.png` - 64x64 version
- `icon_128x128.png` - 128x128 version
- `icon_256x256.png` - 256x256 version
- `icon_512x512.png` - 512x512 version