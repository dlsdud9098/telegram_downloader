#!/usr/bin/env python3

import cv2
import numpy as np

def create_test_image(filename, color, text):
    # Create a 48x48 image
    img = np.ones((48, 48, 3), dtype=np.uint8) * 255
    
    # Draw a circle with the specified color
    center = (24, 24)
    radius = 20
    cv2.circle(img, center, radius, color, -1)
    
    # Add a border
    cv2.circle(img, center, radius, (100, 100, 100), 2)
    
    # Save the image
    cv2.imwrite(filename, img)
    print(f"Created {filename}")

# Create test images
create_test_image("images/not_download.jpg", (0, 0, 255), "Not")  # Red
create_test_image("images/downloading.jpg", (0, 255, 255), "Downloading")  # Yellow
create_test_image("images/downloaded.jpg", (0, 255, 0), "Downloaded")  # Green

print("Test images created successfully!")