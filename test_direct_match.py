#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Template Matching Test
Tests if the templates can match anything at all
"""

import cv2
import numpy as np
import os

print("=" * 60)
print("Direct Template Matching Test")
print("=" * 60)

# Load template
template_path = "images/not_download.jpg"
if not os.path.exists(template_path):
    print(f"Template not found: {template_path}")
    exit(1)

template = cv2.imread(template_path)
if template is None:
    print(f"Failed to load template: {template_path}")
    exit(1)

print(f"Template loaded: {template.shape}")
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# Create test cases
print("\nTest 1: Matching template with itself")
print("-" * 40)

# Test 1: Match template with itself (should be 1.0)
result = cv2.matchTemplate(template_gray, template_gray, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
print(f"Self-match score: {max_val:.4f} (should be 1.0)")

# Test 2: Match template with scaled version
print("\nTest 2: Matching with scaled versions")
print("-" * 40)

scales = [0.8, 0.9, 1.0, 1.1, 1.2]
for scale in scales:
    scaled_h = int(template_gray.shape[0] * scale)
    scaled_w = int(template_gray.shape[1] * scale)
    
    if scaled_h < template_gray.shape[0] or scaled_w < template_gray.shape[1]:
        continue  # Skip if smaller
    
    # Create scaled image
    scaled_img = cv2.resize(template_gray, (scaled_w, scaled_h))
    
    # Match template with scaled version
    result = cv2.matchTemplate(scaled_img, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f"Scale {scale}: max_score = {max_val:.4f}")

# Test 3: Add noise to template
print("\nTest 3: Matching with noise")
print("-" * 40)

noise_levels = [0, 5, 10, 20, 30]
for noise_level in noise_levels:
    # Create noisy version
    noisy = template_gray.copy().astype(np.float32)
    noise = np.random.normal(0, noise_level, noisy.shape)
    noisy = np.clip(noisy + noise, 0, 255).astype(np.uint8)
    
    # Create larger image with noisy template
    test_img = np.ones((100, 100), dtype=np.uint8) * 128
    y_offset = (100 - template_gray.shape[0]) // 2
    x_offset = (100 - template_gray.shape[1]) // 2
    test_img[y_offset:y_offset+template_gray.shape[0], 
             x_offset:x_offset+template_gray.shape[1]] = noisy
    
    # Match
    result = cv2.matchTemplate(test_img, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f"Noise level {noise_level}: max_score = {max_val:.4f}")

# Test 4: Different matching methods
print("\nTest 4: Different matching methods")
print("-" * 40)

# Create test image with template
test_img = np.ones((100, 100), dtype=np.uint8) * 128
y_offset = (100 - template_gray.shape[0]) // 2
x_offset = (100 - template_gray.shape[1]) // 2
test_img[y_offset:y_offset+template_gray.shape[0], 
         x_offset:x_offset+template_gray.shape[1]] = template_gray

methods = [
    ('TM_CCOEFF', cv2.TM_CCOEFF),
    ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
    ('TM_CCORR', cv2.TM_CCORR),
    ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED),
    ('TM_SQDIFF', cv2.TM_SQDIFF),
    ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED)
]

for method_name, method in methods:
    result = cv2.matchTemplate(test_img, template_gray, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        score = min_val
        location = min_loc
        print(f"{method_name}: score = {score:.4f} (lower is better)")
    else:
        score = max_val
        location = max_loc
        print(f"{method_name}: score = {score:.4f} (higher is better)")

print("\n" + "=" * 60)
print("Analysis:")
print("- If self-match is not 1.0, template may be corrupted")
print("- If scores are very low, template may not be representative")
print("- Try using the method with best scores")
print("=" * 60)