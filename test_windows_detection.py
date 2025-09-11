#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Detection Test
Tests template matching with Windows-specific adjustments
"""

import cv2
import numpy as np
import platform
import os
import sys

print("=" * 60)
print("Windows Detection Test")
print("=" * 60)
print(f"Platform: {platform.system()}")
print(f"OpenCV Version: {cv2.__version__}")
print()

# Test with different thresholds
base_threshold = 0.5

if platform.system() == 'Windows':
    # Apply Windows-specific adjustment
    threshold = base_threshold * 0.5
    print(f"Applying Windows adjustment: {base_threshold} -> {threshold}")
else:
    threshold = base_threshold
    print(f"Using standard threshold: {threshold}")

print("\nLoading templates...")
templates = {
    'not_downloaded': 'images/not_download.jpg',
    'downloading': 'images/downloading.jpg',
    'downloaded': 'images/downloaded.jpg'
}

loaded_templates = {}
for name, path in templates.items():
    if os.path.exists(path):
        img = cv2.imread(path)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            loaded_templates[name] = gray
            print(f"✓ Loaded {name}: {gray.shape}")
        else:
            print(f"✗ Failed to load {name}")
    else:
        print(f"✗ Not found: {path}")

if not loaded_templates:
    print("\nNo templates loaded! Exiting.")
    sys.exit(1)

# Check if debug images exist from actual run
if os.path.exists("debug_screen_gray.jpg"):
    print("\n" + "=" * 60)
    print("Testing with captured screen...")
    
    screen = cv2.imread("debug_screen_gray.jpg", cv2.IMREAD_GRAYSCALE)
    if screen is not None:
        print(f"Screen loaded: {screen.shape}")
        
        for name, template in loaded_templates.items():
            print(f"\nTesting {name}:")
            
            # Try multiple methods
            methods = [
                ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
                ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED),
                ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED)
            ]
            
            best_score = 0
            best_method = None
            
            for method_name, method in methods:
                result = cv2.matchTemplate(screen, template, method)
                
                if method == cv2.TM_SQDIFF_NORMED:
                    score = 1 - np.min(result)
                else:
                    score = np.max(result)
                
                print(f"  {method_name}: score = {score:.4f}")
                
                if score > best_score:
                    best_score = score
                    best_method = method_name
            
            # Calculate actual threshold
            if platform.system() == 'Windows':
                actual_threshold = threshold * 0.6
            else:
                actual_threshold = threshold * 0.7
            
            print(f"  Best: {best_method} with score {best_score:.4f}")
            print(f"  Threshold: {actual_threshold:.4f}")
            
            if best_score >= actual_threshold:
                print(f"  ✓ MATCH FOUND!")
            else:
                print(f"  ✗ No match (score {best_score:.4f} < threshold {actual_threshold:.4f})")
                print(f"  Recommendation: Lower threshold or recapture templates")

print("\n" + "=" * 60)
print("Recommendations for Windows users:")
print("1. If no matches found, run main.py once to generate debug images")
print("2. Check debug_screen_capture.jpg - is Telegram visible correctly?")
print("3. If scores are low (< 0.15), recapture templates from YOUR Telegram")
print("4. If scores are moderate (0.15-0.30), threshold adjustment in detector.py helped")
print("5. Consider using PNG format instead of JPEG for templates")
print("=" * 60)