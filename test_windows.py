#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows compatibility test script
Run this to check if all components work on Windows
"""

import sys
import platform

print("=" * 60)
print("Windows Compatibility Test")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Platform: {platform.system()}")
print(f"Platform version: {platform.version()}")
print()

# Test imports
print("Testing imports...")
try:
    import cv2
    print("✓ OpenCV imported successfully")
except ImportError as e:
    print(f"✗ OpenCV import failed: {e}")

try:
    import pyautogui
    print("✓ PyAutoGUI imported successfully")
    print(f"  Screen size: {pyautogui.size()}")
except ImportError as e:
    print(f"✗ PyAutoGUI import failed: {e}")
except Exception as e:
    print(f"✗ PyAutoGUI error: {e}")

try:
    import mss
    print("✓ MSS imported successfully")
    with mss.mss() as sct:
        monitors = sct.monitors
        print(f"  Found {len(monitors)-1} monitor(s)")
except ImportError as e:
    print(f"✗ MSS import failed: {e}")
except Exception as e:
    print(f"✗ MSS error: {e}")

try:
    import customtkinter
    print("✓ CustomTkinter imported successfully")
except ImportError as e:
    print(f"✗ CustomTkinter import failed: {e}")

try:
    import numpy
    print("✓ NumPy imported successfully")
except ImportError as e:
    print(f"✗ NumPy import failed: {e}")

try:
    from PIL import Image
    print("✓ PIL imported successfully")
except ImportError as e:
    print(f"✗ PIL import failed: {e}")

print()
print("Testing screen capture...")
try:
    import mss
    with mss.mss() as sct:
        # Capture a small region
        region = {"top": 100, "left": 100, "width": 200, "height": 200}
        screenshot = sct.grab(region)
        print(f"✓ Screen capture successful: {screenshot.width}x{screenshot.height}")
except Exception as e:
    print(f"✗ Screen capture failed: {e}")

print()
print("Testing PyAutoGUI...")
try:
    import pyautogui
    # Get current mouse position
    x, y = pyautogui.position()
    print(f"✓ Mouse position: ({x}, {y})")
    
    # Test failsafe
    pyautogui.FAILSAFE = True
    print("✓ PyAutoGUI failsafe enabled")
except Exception as e:
    print(f"✗ PyAutoGUI test failed: {e}")

print()
print("Testing template loading...")
try:
    import cv2
    import os
    
    template_paths = [
        'images/not_download.jpg',
        'images/downloading.jpg',
        'images/downloaded.jpg'
    ]
    
    for path in template_paths:
        if os.path.exists(path):
            img = cv2.imread(path)
            if img is not None:
                h, w = img.shape[:2]
                print(f"✓ Loaded {path}: {w}x{h}")
            else:
                print(f"✗ Failed to load {path}")
        else:
            print(f"✗ File not found: {path}")
except Exception as e:
    print(f"✗ Template loading failed: {e}")

print()
print("=" * 60)
print("Test complete. Check for any errors above.")
print("If all tests pass, the application should work on Windows.")
print("=" * 60)