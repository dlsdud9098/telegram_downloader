#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Platform Difference Analysis
Compares image detection between Ubuntu and Windows
"""

import cv2
import numpy as np
import platform
import os

print("=" * 60)
print("Platform Difference Analysis")
print("=" * 60)
print(f"Platform: {platform.system()}")
print(f"OpenCV Version: {cv2.__version__}")
print()

# Load template
template_path = "images/not_download.jpg"
if os.path.exists(template_path):
    template = cv2.imread(template_path)
    print(f"Template loaded: {template.shape if template is not None else 'Failed'}")
    
    if template is not None:
        # Check color space
        print(f"Template dtype: {template.dtype}")
        print(f"Template min/max: {template.min()}/{template.max()}")
        
        # Convert to grayscale
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        print(f"Gray template shape: {gray_template.shape}")
        print(f"Gray template dtype: {gray_template.dtype}")
        print(f"Gray template min/max: {gray_template.min()}/{gray_template.max()}")
        
        # Save processed template for comparison
        cv2.imwrite(f"template_processed_{platform.system()}.jpg", gray_template)
        print(f"Saved processed template as: template_processed_{platform.system()}.jpg")
        
        # Test different matching methods
        print("\nTesting matching methods:")
        methods = [
            ('TM_CCOEFF', cv2.TM_CCOEFF),
            ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
            ('TM_CCORR', cv2.TM_CCORR),
            ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED),
            ('TM_SQDIFF', cv2.TM_SQDIFF),
            ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED)
        ]
        
        # Create a test image (simulated screen)
        test_img = np.ones((200, 200), dtype=np.uint8) * 128
        # Place template in center
        y_offset = (200 - gray_template.shape[0]) // 2
        x_offset = (200 - gray_template.shape[1]) // 2
        test_img[y_offset:y_offset+gray_template.shape[0], 
                 x_offset:x_offset+gray_template.shape[1]] = gray_template
        
        for method_name, method in methods:
            result = cv2.matchTemplate(test_img, gray_template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                match_val = min_val
                match_loc = min_loc
            else:
                match_val = max_val
                match_loc = max_loc
            
            print(f"  {method_name}: value={match_val:.4f}, location={match_loc}")
        
        print("\nPlatform-specific issues to check:")
        print("1. DPI Scaling:")
        print("   - Windows often has DPI scaling (125%, 150%)")
        print("   - Ubuntu typically uses 100% scaling")
        print("   Solution: Capture templates on the same system")
        
        print("\n2. Color Profile:")
        print("   - Windows and Linux may use different color profiles")
        print("   - This affects RGB values slightly")
        
        print("\n3. Font Rendering:")
        print("   - Windows uses ClearType")
        print("   - Linux uses different font rendering")
        print("   - Telegram icons may look slightly different")
        
        print("\n4. Image Compression:")
        print("   - JPEG compression artifacts may differ")
        print("   - Use PNG for templates instead of JPEG")
        
        print("\nRecommendations:")
        print("1. Create platform-specific templates:")
        print("   - images/windows/not_download.jpg")
        print("   - images/linux/not_download.jpg")
        print("2. Or use PNG format for better consistency")
        print("3. Lower the matching threshold (currently 0.6)")
        print("4. Test with multiple matching methods")
        
else:
    print(f"Template not found: {template_path}")