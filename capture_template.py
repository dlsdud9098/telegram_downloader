#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Capture Tool
Use this to capture new template images from Telegram
"""

import cv2
import numpy as np
from PIL import ImageGrab
import os
import time

def capture_screen_region():
    """Capture a region of the screen"""
    print("=" * 60)
    print("Template Capture Tool")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Open Telegram Desktop")
    print("2. Navigate to a channel with files")
    print("3. Position the window so you can see download buttons")
    print("4. This tool will capture the screen in 3 seconds")
    print()
    
    input("Press Enter when ready...")
    print("Capturing in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    
    # Capture full screen
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Save full screenshot
    cv2.imwrite("full_screenshot.png", screenshot_cv)
    print("\nFull screenshot saved as 'full_screenshot.png'")
    
    # Show instructions for cropping
    print("\nNow you need to:")
    print("1. Open 'full_screenshot.png' in an image editor")
    print("2. Crop JUST the download button icons:")
    print("   - not_download.jpg: The download arrow (↓)")
    print("   - downloading.jpg: The progress circle")
    print("   - downloaded.jpg: The checkmark (✓)")
    print("3. Save each as a small image (40-60 pixels)")
    print("4. Place them in the 'images' folder")
    
    # Optional: Interactive cropping
    print("\nWould you like to crop interactively? (y/n)")
    if input().lower() == 'y':
        crop_interactive(screenshot_cv)

def crop_interactive(image):
    """Interactive cropping tool"""
    print("\nInteractive Cropping:")
    print("- Click and drag to select region")
    print("- Press 's' to save selection")
    print("- Press 'q' to quit")
    print("- Press 'r' to reset")
    
    # Global variables for mouse callback
    selecting = False
    start_x, start_y = 0, 0
    end_x, end_y = 0, 0
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal selecting, start_x, start_y, end_x, end_y
        
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            start_x, start_y = x, y
            end_x, end_y = x, y
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if selecting:
                end_x, end_y = x, y
                
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            end_x, end_y = x, y
    
    # Create window
    cv2.namedWindow('Crop Template', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Crop Template', mouse_callback)
    
    template_count = 1
    
    while True:
        # Copy image for drawing
        display = image.copy()
        
        # Draw rectangle if selecting
        if start_x != end_x and start_y != end_y:
            cv2.rectangle(display, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            # Show size
            width = abs(end_x - start_x)
            height = abs(end_y - start_y)
            cv2.putText(display, f"{width}x{height}", (start_x, start_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow('Crop Template', display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save selection
            if start_x != end_x and start_y != end_y:
                # Get coordinates
                x1, x2 = min(start_x, end_x), max(start_x, end_x)
                y1, y2 = min(start_y, end_y), max(start_y, end_y)
                
                # Crop image
                cropped = image[y1:y2, x1:x2]
                
                # Save
                filename = f"template_{template_count}.jpg"
                cv2.imwrite(filename, cropped)
                print(f"Saved {filename} ({x2-x1}x{y2-y1} pixels)")
                template_count += 1
                
                # Reset selection
                start_x, start_y = 0, 0
                end_x, end_y = 0, 0
        elif key == ord('r'):
            # Reset selection
            start_x, start_y = 0, 0
            end_x, end_y = 0, 0
    
    cv2.destroyAllWindows()
    print("\nTemplates saved. Rename them to:")
    print("- not_download.jpg (for download button)")
    print("- downloading.jpg (for progress indicator)")
    print("- downloaded.jpg (for completed/checkmark)")

if __name__ == "__main__":
    try:
        capture_screen_region()
    except ImportError:
        print("Error: PIL/Pillow not installed")
        print("Install with: pip install Pillow")
    except Exception as e:
        print(f"Error: {e}")