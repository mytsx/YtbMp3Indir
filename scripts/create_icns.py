#!/usr/bin/env python3
"""
PNG'den macOS ICNS icon dosyası oluştur
"""

import sys
import os
import subprocess
from PIL import Image

def create_icns(input_png, output_icns):
    """PNG dosyasından ICNS oluştur"""
    
    # PNG dosyasını kontrol et
    if not os.path.exists(input_png):
        print(f"Hata: {input_png} bulunamadı!")
        return False
    
    # Geçici iconset klasörü oluştur
    iconset_dir = output_icns.replace('.icns', '.iconset')
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Gereken boyutlar
    sizes = [
        (16, 16, "16x16"),
        (32, 32, "16x16@2x"),
        (32, 32, "32x32"),
        (64, 64, "32x32@2x"),
        (128, 128, "128x128"),
        (256, 256, "128x128@2x"),
        (256, 256, "256x256"),
        (512, 512, "256x256@2x"),
        (512, 512, "512x512"),
        (1024, 1024, "512x512@2x"),
    ]
    
    # PNG'yi aç
    try:
        img = Image.open(input_png)
        
        # RGBA'ya çevir
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Her boyut için resim oluştur
        for width, height, name in sizes:
            resized = img.resize((width, height), Image.Resampling.LANCZOS)
            resized.save(os.path.join(iconset_dir, f"icon_{name}.png"))
            print(f"✓ {name} oluşturuldu")
        
        # iconutil ile ICNS oluştur
        cmd = ['iconutil', '-c', 'icns', iconset_dir, '-o', output_icns]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ ICNS başarıyla oluşturuldu: {output_icns}")
            # Geçici klasörü temizle
            subprocess.run(['rm', '-rf', iconset_dir])
            return True
        else:
            print(f"\n❌ ICNS oluşturulamadı: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Kullanım: python create_icns.py input.png output.icns")
        sys.exit(1)
    
    input_png = sys.argv[1]
    output_icns = sys.argv[2]
    
    if create_icns(input_png, output_icns):
        sys.exit(0)
    else:
        sys.exit(1)