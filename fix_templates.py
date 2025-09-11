#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Template Sizes
Resize templates to optimal size for detection
"""

import cv2
import os

print("=" * 60)
print("Template Size Fixer")
print("=" * 60)

# Common icon sizes in Telegram
sizes_to_try = [
    (20, 20),  # Very small
    (24, 24),  # Small icon
    (32, 32),  # Medium icon
    (40, 40),  # Large icon
    (48, 48),  # Extra large
    (50, 50),  # Current size
    (64, 64),  # Larger
]

template_files = [
    "images/not_download.jpg",
    "images/downloading.jpg", 
    "images/downloaded.jpg"
]

print("\nCurrent template sizes:")
for file in template_files:
    if os.path.exists(file):
        img = cv2.imread(file)
        if img is not None:
            h, w = img.shape[:2]
            print(f"  {file}: {w}x{h}")

print("\nCreating multiple sized versions...")
for file in template_files:
    if os.path.exists(file):
        img = cv2.imread(file)
        if img is not None:
            base_name = os.path.basename(file).replace('.jpg', '')
            
            # Create sized versions
            for width, height in sizes_to_try:
                resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
                output_name = f"images/{base_name}_{width}x{height}.jpg"
                cv2.imwrite(output_name, resized)
                print(f"  Created: {output_name}")

print("\n" + "=" * 60)
print("Instructions:")
print("1. Try different sized templates to see which works best")
print("2. Copy the best ones over the originals:")
print("   copy images\\not_download_32x32.jpg images\\not_download.jpg")
print("3. Or use original full-size images:")
print("   copy images_original\\*.jpg images\\")
print("=" * 60)