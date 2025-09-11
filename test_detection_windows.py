#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Image Detection Test
Run this to debug image detection issues on Windows
"""

import os
import cv2
import numpy as np
from pathlib import Path

print("=" * 60)
print("Windows Image Detection Debug")
print("=" * 60)

# Check current directory
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
print()

# Check images folder
if os.path.exists('images'):
    print("Images folder found!")
    print(f"Contents: {os.listdir('images')}")
else:
    print("ERROR: Images folder not found!")
    print("Make sure to run this script from the telegram_downloader directory")
print()

# Test image paths
templates = {
    'not_download': 'images/not_download.jpg',
    'downloading': 'images/downloading.jpg',
    'downloaded': 'images/downloaded.jpg'
}

print("Testing image loading:")
for name, path in templates.items():
    print(f"\n{name}: {path}")
    
    # Check if file exists
    if os.path.exists(path):
        print(f"  ✓ File exists")
        
        # Try absolute path
        abs_path = os.path.abspath(path)
        print(f"  Absolute path: {abs_path}")
        
        # Try loading with cv2
        img = cv2.imread(path)
        if img is not None:
            h, w, c = img.shape
            print(f"  ✓ Loaded with cv2: {w}x{h}, {c} channels")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            print(f"  ✓ Converted to grayscale: {gray.shape}")
        else:
            print(f"  ✗ Failed to load with cv2.imread()")
            
            # Try alternative loading
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                    print(f"  File size: {len(data)} bytes")
                    
                # Try loading with numpy
                nparr = np.frombuffer(data, np.uint8)
                img2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img2 is not None:
                    print(f"  ✓ Loaded with cv2.imdecode: {img2.shape}")
                else:
                    print(f"  ✗ Failed with cv2.imdecode")
            except Exception as e:
                print(f"  ✗ Error reading file: {e}")
    else:
        print(f"  ✗ File not found")
        
        # Try Windows path
        win_path = path.replace('/', '\\')
        if os.path.exists(win_path):
            print(f"  ✓ Found with Windows path: {win_path}")
        else:
            print(f"  ✗ Not found with Windows path either")

print()
print("=" * 60)
print("Recommendations:")
print("1. Make sure images folder is in the same directory as the script")
print("2. Check that image files are valid JPEG files")
print("3. Try using smaller template images (50x50 pixels)")
print("4. If running from executable, ensure images folder is next to .exe")
print("=" * 60)