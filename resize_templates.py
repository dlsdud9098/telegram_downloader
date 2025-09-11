#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Resizer for Telegram Auto Downloader
Resizes template images to appropriate size for detection
"""

import cv2
import os
from pathlib import Path

def resize_templates():
    """Resize template images to smaller size suitable for detection"""
    
    template_dir = Path("images")
    output_dir = Path("images_resized")
    output_dir.mkdir(exist_ok=True)
    
    # Target size for templates (should be just the icon, not the whole screenshot)
    TARGET_SIZE = 50  # 50x50 pixels is typical for a button/icon
    
    templates = {
        'not_download.jpg': 'Template for not downloaded state',
        'downloading.jpg': 'Template for downloading state',
        'downloaded.jpg': 'Template for downloaded/completed state'
    }
    
    print("Current template sizes:")
    print("-" * 50)
    
    for filename, description in templates.items():
        filepath = template_dir / filename
        if filepath.exists():
            img = cv2.imread(str(filepath))
            h, w = img.shape[:2]
            print(f"{filename}: {w}x{h} pixels")
            
            # Save a resized version
            resized = cv2.resize(img, (TARGET_SIZE, TARGET_SIZE))
            output_path = output_dir / filename
            cv2.imwrite(str(output_path), resized)
            print(f"  -> Resized to {TARGET_SIZE}x{TARGET_SIZE} saved to {output_path}")
        else:
            print(f"{filename}: NOT FOUND")
    
    print("\n" + "="*70)
    print("IMPORTANT: The current templates appear to be full screenshots.")
    print("For best results, you should:")
    print("1. Take a screenshot of JUST the download button/icon")
    print("2. Crop to show only the icon (typically 30-60 pixels)")
    print("3. Save three states:")
    print("   - not_download.jpg: The download arrow icon")
    print("   - downloading.jpg: The progress/loading icon")
    print("   - downloaded.jpg: The checkmark/completed icon")
    print("\nExample: The download button should be cropped like this:")
    print("   [↓] <- Just this icon, not the whole message")
    print("\nThe resized versions in 'images_resized/' are auto-generated")
    print("but may not work well. Manual cropping is recommended.")
    print("="*70)

def show_template_guide():
    """Display a visual guide for creating templates"""
    
    print("\nTemplate Creation Guide:")
    print("------------------------")
    print("""
1. Open Telegram Desktop
2. Find messages with different download states:
   - A file that hasn't been downloaded (shows ↓ arrow)
   - A file currently downloading (shows progress circle)
   - A file already downloaded (shows checkmark or document icon)

3. Use a screenshot tool to capture ONLY the icon:
   - On Linux: Use 'gnome-screenshot -a' or 'scrot -s'
   - On Windows: Use Snipping Tool (Win+Shift+S)
   - On macOS: Use Command+Shift+4

4. Crop to include just the icon with a bit of padding (5-10 pixels)
   Ideal size: 40x40 to 60x60 pixels

5. Save as:
   - images/not_download.jpg
   - images/downloading.jpg  
   - images/downloaded.jpg

Note: The templates should be consistent in size and cropping.
""")

if __name__ == "__main__":
    resize_templates()
    show_template_guide()