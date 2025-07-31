#!/usr/bin/env python3
"""
Complete icon processing pipeline:
1. Remove white background
2. Crop to remove extra space
3. Create all sizes
"""

import sys
import os

# Add parent directory to path to import other scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.process_icon_transparent import process_icon_transparent, create_icon_sizes
from scripts.crop_icon import crop_icon, save_cropped_icons

def process_complete_pipeline(input_image='image.png'):
    """Run complete icon processing pipeline"""
    
    print(f"Starting complete icon processing for: {input_image}")
    print("-" * 50)
    
    # Step 1: Make transparent
    print("\nStep 1: Removing white background...")
    transparent_img = process_icon_transparent(input_image)
    
    if not transparent_img:
        print("Failed to process image!")
        return
    
    # Save intermediate result
    transparent_img.save('assets/icon_transparent_uncropped.png', 'PNG')
    
    # Step 2: Crop
    print("\nStep 2: Cropping extra transparent space...")
    cropped_img = crop_icon('assets/icon_transparent_uncropped.png')
    
    if not cropped_img:
        print("Failed to crop image!")
        return
    
    # Step 3: Save final icons
    print("\nStep 3: Creating final icon set...")
    save_cropped_icons(cropped_img, 'icon')
    
    # Clean up intermediate file
    if os.path.exists('assets/icon_transparent_uncropped.png'):
        os.remove('assets/icon_transparent_uncropped.png')
    
    print("\n" + "=" * 50)
    print("Icon processing complete!")
    print("Final icons saved in assets/ directory")

if __name__ == "__main__":
    # Get input image from command line or use default
    input_image = sys.argv[1] if len(sys.argv) > 1 else 'image.png'
    
    # Run the complete pipeline
    process_complete_pipeline(input_image)