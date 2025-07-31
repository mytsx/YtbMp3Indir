#!/usr/bin/env python3
"""
Process icon to remove white background and make it transparent
Usage: python scripts/process_icon_transparent.py [image_path]
"""

from PIL import Image
import numpy as np
import os
import sys

def process_icon_transparent(image_path='image.png'):
    """Remove white background from icon and make it transparent"""
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found!")
        print("Usage: python scripts/process_icon_transparent.py [image_path]")
        return
    
    print(f"Processing {image_path}...")
    
    # Open and convert to RGBA
    img = Image.open(image_path)
    img = img.convert("RGBA")
    data = np.array(img)
    
    # Create new image array
    new_data = np.array(data)
    
    # Process each pixel
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            r, g, b, a = data[y, x]
            
            # If pixel is white or near-white (with tolerance)
            # Make it transparent
            if r > 240 and g > 240 and b > 240:
                new_data[y, x] = [r, g, b, 0]  # Make transparent
            else:
                new_data[y, x] = [r, g, b, 255]  # Keep original with full opacity
    
    # Convert back to image
    new_img = Image.fromarray(new_data, 'RGBA')
    
    # Create output directory
    os.makedirs('assets', exist_ok=True)
    
    # Save processed image
    new_img.save('assets/icon_transparent.png', 'PNG')
    print("Saved transparent icon to: assets/icon_transparent.png")
    
    return new_img

def create_icon_sizes(img, output_name='icon'):
    """Create various icon sizes from the processed image"""
    
    # Save main icon
    img.save(f'assets/{output_name}.png', 'PNG')
    print(f"Saved main icon: assets/{output_name}.png")
    
    # Create various sizes
    sizes = [16, 32, 48, 64, 128, 256, 512]
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'assets/{output_name}_{size}x{size}.png', 'PNG')
        print(f"Created {size}x{size} icon")

if __name__ == "__main__":
    # Get image path from command line or use default
    image_path = sys.argv[1] if len(sys.argv) > 1 else 'image.png'
    
    # Process the icon
    processed_img = process_icon_transparent(image_path)
    
    if processed_img:
        create_icon_sizes(processed_img)
        print("\nIcon processing complete!")
        print("Original design preserved with white background removed.")