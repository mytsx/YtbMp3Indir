#!/usr/bin/env python3
"""
Crop icon to remove extra transparent space
Usage: python scripts/crop_icon.py [icon_path]
"""

from PIL import Image
import os
import sys

def crop_icon(icon_path='assets/icon.png'):
    """Crop icon to remove transparent borders"""
    
    if not os.path.exists(icon_path):
        print(f"Error: {icon_path} not found!")
        return
    
    print(f"Cropping {icon_path}...")
    
    # Load the icon
    img = Image.open(icon_path)
    img = img.convert("RGBA")
    
    # Get the bounding box of non-transparent pixels
    bbox = img.getbbox()
    
    if bbox:
        # Crop the image to the bounding box
        cropped = img.crop(bbox)
        
        # Make it square by padding if needed
        width, height = cropped.size
        if width != height:
            # Create a new square image
            size = max(width, height)
            square_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # Paste the cropped image in the center
            x = (size - width) // 2
            y = (size - height) // 2
            square_img.paste(cropped, (x, y))
            cropped = square_img
        
        print(f"Cropped to: {cropped.size}")
        return cropped
    else:
        print("Could not determine bounding box")
        return None

def save_cropped_icons(cropped_img, base_name='icon'):
    """Save cropped icon in various sizes"""
    
    # Save the cropped icon
    cropped_img.save(f'assets/{base_name}.png', 'PNG')
    print(f"Saved cropped icon: assets/{base_name}.png")
    
    # Recreate various sizes
    sizes = [16, 32, 48, 64, 128, 256, 512]
    for size in sizes:
        resized = cropped_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'assets/{base_name}_{size}x{size}.png', 'PNG')
        print(f"Created {size}x{size} icon")

if __name__ == "__main__":
    # Get icon path from command line or use default
    icon_path = sys.argv[1] if len(sys.argv) > 1 else 'assets/icon.png'
    
    # Crop the icon
    cropped = crop_icon(icon_path)
    
    if cropped:
        save_cropped_icons(cropped)
        print("\nIcon cropping complete!")
        print("Extra transparent space removed.")