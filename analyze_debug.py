#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Debug Images
Check what's being captured vs templates
"""

import cv2
import numpy as np
import os

print("=" * 60)
print("Debug Image Analysis")
print("=" * 60)

# Check if debug images exist
debug_files = [
    "debug_screen_capture.jpg",
    "debug_screen_gray.jpg",
    "debug_template_not_downloaded.jpg",
    "debug_template_downloading.jpg",
    "debug_template_downloaded.jpg"
]

print("\nChecking for debug files...")
for file in debug_files:
    if os.path.exists(file):
        print(f"✓ Found: {file}")
        img = cv2.imread(file)
        if img is not None:
            print(f"  Size: {img.shape}")
    else:
        print(f"✗ Missing: {file}")

# If screen capture exists, analyze it
if os.path.exists("debug_screen_gray.jpg"):
    print("\n" + "=" * 60)
    print("Analyzing captured screen...")
    
    screen = cv2.imread("debug_screen_gray.jpg", cv2.IMREAD_GRAYSCALE)
    template = cv2.imread("images/not_download.jpg", cv2.IMREAD_GRAYSCALE)
    
    if screen is not None and template is not None:
        print(f"Screen size: {screen.shape}")
        print(f"Template size: {template.shape}")
        
        # Try matching at different scales
        print("\nTrying different template scales...")
        scales = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        
        best_scale = 1.0
        best_score = 0
        best_location = (0, 0)
        
        for scale in scales:
            # Resize template
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            
            if width > screen.shape[1] or height > screen.shape[0]:
                continue
                
            resized = cv2.resize(template, (width, height))
            
            # Match
            result = cv2.matchTemplate(screen, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            print(f"  Scale {scale:.2f} ({width}x{height}): max_score = {max_val:.4f}")
            
            if max_val > best_score:
                best_score = max_val
                best_scale = scale
                best_location = max_loc
        
        print(f"\nBest match: scale={best_scale}, score={best_score:.4f}, location={best_location}")
        
        if best_score > 0.5:
            print("✓ Found a match! The template needs to be scaled.")
            print(f"Recommendation: Resize template to {int(template.shape[1]*best_scale)}x{int(template.shape[0]*best_scale)} pixels")
        else:
            print("✗ No good match found even with scaling.")
            print("Possible issues:")
            print("1. Template doesn't match what's on screen")
            print("2. Telegram theme is different (dark/light)")
            print("3. Different Telegram version or UI")
            
            # Show histogram comparison
            print("\nHistogram analysis:")
            hist_screen = cv2.calcHist([screen], [0], None, [256], [0, 256])
            hist_template = cv2.calcHist([template], [0], None, [256], [0, 256])
            
            # Normalize histograms
            hist_screen = hist_screen / hist_screen.sum()
            hist_template = hist_template / hist_template.sum()
            
            # Compare histograms
            correlation = cv2.compareHist(hist_screen, hist_template, cv2.HISTCMP_CORREL)
            print(f"Histogram correlation: {correlation:.4f}")
            
            if correlation < 0.5:
                print("⚠ Very different brightness/contrast between template and screen")
                print("Try capturing new templates from the current Telegram window")

print("\n" + "=" * 60)
print("Recommendations:")
print("1. Run program once to generate debug images")
print("2. Run this script to analyze them")
print("3. Check if debug_screen_capture.jpg shows Telegram correctly")
print("4. If template scale is wrong, resize accordingly")
print("=" * 60)