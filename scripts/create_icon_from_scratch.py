#!/usr/bin/env python3
"""
Create MP3 downloader icon from scratch using PIL
This creates a red circle with white music note and download arrow
"""

from PIL import Image, ImageDraw
import os

def create_icon_from_scratch(size=512):
    """Create the icon design from scratch"""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw red circle (YouTube-like red)
    circle_color = (221, 75, 57, 255)
    draw.ellipse([0, 0, size-1, size-1], fill=circle_color)
    
    # White color for icons
    white = (255, 255, 255, 255)
    
    # Music note parameters
    note_center_x = size * 0.4
    note_center_y = size * 0.35
    note_width = size * 0.08
    note_height = size * 0.06
    
    # Draw note head (ellipse)
    draw.ellipse([
        note_center_x - note_width,
        note_center_y - note_height,
        note_center_x + note_width,
        note_center_y + note_height
    ], fill=white)
    
    # Draw note stem
    stem_width = size * 0.015
    stem_height = size * 0.2
    stem_x = note_center_x + note_width - stem_width/2
    draw.rectangle([
        stem_x,
        note_center_y - stem_height,
        stem_x + stem_width,
        note_center_y
    ], fill=white)
    
    # Draw note flag
    flag_points = [
        (stem_x + stem_width, note_center_y - stem_height),
        (stem_x + stem_width + size * 0.08, note_center_y - stem_height + size * 0.03),
        (stem_x + stem_width + size * 0.07, note_center_y - stem_height + size * 0.08),
        (stem_x + stem_width, note_center_y - stem_height + size * 0.05)
    ]
    draw.polygon(flag_points, fill=white)
    
    # Draw download arrow
    arrow_center_x = size * 0.5
    arrow_top_y = size * 0.55
    arrow_width = size * 0.25
    arrow_shaft_width = size * 0.08
    arrow_shaft_height = size * 0.15
    arrow_head_height = size * 0.1
    
    # Draw arrow shaft
    draw.rectangle([
        arrow_center_x - arrow_shaft_width/2,
        arrow_top_y,
        arrow_center_x + arrow_shaft_width/2,
        arrow_top_y + arrow_shaft_height
    ], fill=white)
    
    # Draw arrow head (triangle)
    arrow_points = [
        (arrow_center_x - arrow_width/2, arrow_top_y + arrow_shaft_height - size * 0.02),
        (arrow_center_x + arrow_width/2, arrow_top_y + arrow_shaft_height - size * 0.02),
        (arrow_center_x, arrow_top_y + arrow_shaft_height + arrow_head_height)
    ]
    draw.polygon(arrow_points, fill=white)
    
    return img

def save_all_icon_sizes(img, base_name='icon'):
    """Save icon in all required sizes"""
    
    # Create assets directory
    os.makedirs('assets', exist_ok=True)
    
    # Save main icon
    img.save(f'assets/{base_name}.png', 'PNG')
    print(f"Created main icon: assets/{base_name}.png")
    
    # Create various sizes
    sizes = [16, 32, 48, 64, 128, 256]
    for icon_size in sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        resized.save(f'assets/{base_name}_{icon_size}x{icon_size}.png', 'PNG')
        print(f"Created {icon_size}x{icon_size} icon")

if __name__ == "__main__":
    print("Creating MP3 downloader icon from scratch...")
    
    # Create the icon
    icon = create_icon_from_scratch(512)
    
    # Save all sizes
    save_all_icon_sizes(icon)
    
    print("\nIcon creation complete!")
    print("Created custom icon with music note and download arrow")