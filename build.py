#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for creating standalone executable
"""

import os
import sys
import shutil
import platform
import subprocess

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    system = platform.system()
    print(f"Building for {system}...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Single file executable
        "--console",  # Console window (for debugging output)
        "--name", f"TelegramAutoDownloader_{system}",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
    ]
    
    # Add data files
    cmd.extend(["--add-data", f"images{os.pathsep}images"])
    cmd.extend(["--add-data", f"README.md{os.pathsep}."])
    
    # Hidden imports for all dependencies
    hidden_imports = [
        "PIL._tkinter_finder",
        "customtkinter",
        "cv2",
        "numpy",
        "mss",
        "pyautogui",
        "pynput",
        "pynput.keyboard",
        "pynput.mouse",
    ]
    
    # Platform-specific hidden imports
    if system == "Windows":
        hidden_imports.extend([
            "pynput.keyboard._win32",
            "pynput.mouse._win32",
            "win32gui",
            "win32api",
            "win32con",
        ])
    elif system == "Darwin":
        hidden_imports.extend([
            "pynput.keyboard._darwin",
            "pynput.mouse._darwin",
            "Quartz",
            "AppKit",
        ])
    else:  # Linux
        hidden_imports.extend([
            "pynput.keyboard._xorg",
            "pynput.mouse._xorg",
            "Xlib",
        ])
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Add main script
    cmd.append("main.py")
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✓ Build successful!")
        print(f"Executable created: dist/TelegramAutoDownloader_{system}")
        
        # Create distribution folder
        dist_dir = f"telegram_downloader_{system.lower()}"
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir)
        
        # Copy executable
        exe_name = f"TelegramAutoDownloader_{system}"
        if system == "Windows":
            exe_name += ".exe"
        shutil.copy(f"dist/{exe_name}", dist_dir)
        
        # Copy images folder
        shutil.copytree("images", f"{dist_dir}/images")
        
        # Copy README
        shutil.copy("README.md", dist_dir)
        
        # Create run script
        if system == "Windows":
            with open(f"{dist_dir}/run.bat", "w") as f:
                f.write(f"@echo off\n{exe_name}\npause")
        else:
            with open(f"{dist_dir}/run.sh", "w") as f:
                f.write(f"#!/bin/bash\n./{exe_name}")
            os.chmod(f"{dist_dir}/run.sh", 0o755)
        
        print(f"\n✓ Distribution folder created: {dist_dir}")
        print("\nInstructions:")
        print("1. Make sure to prepare template images in the 'images' folder")
        print("2. Run the executable directly or use the run script")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()