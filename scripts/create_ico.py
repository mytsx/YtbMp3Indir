#!/usr/bin/env python3
"""
Create ICO file from PNG icon for Windows
"""

from PIL import Image
import os

def create_ico_from_png():
    """Create Windows ICO file from PNG icon"""
    
    png_path = 'assets/icon.png'
    ico_path = 'assets/icon.ico'
    
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found!")
        return False
    
    try:
        # Open PNG
        img = Image.open(png_path)
        
        # ICO sizes that Windows expects
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Create list of images for ICO
        images = []
        for size in icon_sizes:
            # Resize image
            resized = img.resize(size, Image.Resampling.LANCZOS)
            images.append(resized)
        
        # Save as ICO with multiple sizes
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        print(f"✓ Created {ico_path}")
        print(f"  Sizes: {', '.join([f'{w}x{h}' for w, h in icon_sizes])}")
        
        return True
        
    except Exception as e:
        print(f"Error creating ICO: {e}")
        return False

if __name__ == "__main__":
    create_ico_from_png()