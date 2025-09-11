#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import io
import platform
import cv2

# Set UTF-8 encoding for stdout and stderr (for Windows compatibility)
if platform.system() == 'Windows':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import time
from threading import Thread, Event
from pynput import keyboard
from src.detector import ImageDetector
from src.region_selector import RegionSelector
from src.automation import AutomationController
from src.ui import ControlPanel

class TelegramAutoDownloader:
    def __init__(self):
        self.detector = ImageDetector()
        self.selector = RegionSelector()
        self.automation = AutomationController()
        self.ui = None
        self.stop_event = Event()
        self.worker_thread = None
        self.selected_region = None
        self.keyboard_listener = None
        
        # Settings
        self.settings = {
            'scroll_amount': 3,
            'click_delay': 0.2,
            'scroll_threshold': 20
        }
        
        # Load image templates
        template_paths = {
            'not_downloaded': 'images/not_download.jpg',
            'downloading': 'images/downloading.jpg',
            'downloaded': 'images/downloaded.jpg'
        }
        
        # Check if image files exist and get sizes
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for images in: {template_paths}")
        
        template_sizes = {}
        for name, path in template_paths.items():
            # Use absolute path for better compatibility
            abs_path = os.path.abspath(path)
            print(f"Checking {name}: {abs_path}")
            
            if not os.path.exists(abs_path):
                print(f"WARNING: {abs_path} file not found!")
                # Try alternative paths
                alt_paths = [
                    path,
                    os.path.join(os.path.dirname(__file__), path),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
                ]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        print(f"  Found at alternative path: {alt_path}")
                        template_paths[name] = alt_path
                        abs_path = alt_path
                        break
            
            if os.path.exists(abs_path):
                img = cv2.imread(abs_path)
                if img is not None:
                    h, w = img.shape[:2]
                    template_sizes[name] = (w, h)
                    print(f"  SUCCESS: Loaded '{name}': {w}x{h} pixels")
                else:
                    print(f"  ERROR: Could not read image file {abs_path}")
        
        if template_sizes:
            max_width = max(size[0] for size in template_sizes.values())
            max_height = max(size[1] for size in template_sizes.values())
            print(f"\nIMPORTANT: Select a region at least {max_width}x{max_height} pixels for detection to work properly.\n")
        
        self.detector.load_templates(template_paths)
        
    def select_region(self):
        return self.selector.select_region()
    
    def start_automation(self, region):
        print(f"Starting automation with region: {region}")
        self.selected_region = region
        self.stop_event.clear()
        
        # Start keyboard listener for ESC key
        self._start_keyboard_listener()
        
        self.worker_thread = Thread(target=self._automation_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        print("Worker thread started")
        print("Press ESC key to stop automation at any time")
    
    def stop_automation(self):
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=1)
        self._stop_keyboard_listener()
    
    def _automation_loop(self):
        print("Automation loop started")
        while not self.stop_event.is_set():
            try:
                # Detect images
                print(f"Detecting in region: {self.selected_region}")
                results = self.detector.detect_images(self.selected_region)
                stats = self.detector.get_detection_stats(results)
                print(f"Detection results: {results}")
                
                # UI 업데이트
                if self.ui:
                    self.ui.update_stats(stats)
                    
                    if results['not_downloaded']:
                        self.ui.update_status(f"Clicking {len(results['not_downloaded'])} not downloaded items...")
                    elif stats['downloaded_percentage'] >= 20:
                        self.ui.update_status(f"Completion {stats['downloaded_percentage']:.1f}% - Scrolling...")
                    else:
                        self.ui.update_status("Detecting...")
                
                # Perform automation with settings
                action_performed = self.automation.perform_automation(
                    results, stats, 
                    scroll_amount=self.settings['scroll_amount'],
                    click_delay=self.settings['click_delay'],
                    scroll_threshold=self.settings['scroll_threshold']
                )
                
                # Wait briefly after action
                if action_performed:
                    # Shorter wait for continuous scrolling
                    if stats.get('downloaded_percentage', 0) >= 20 and not results.get('not_downloaded'):
                        time.sleep(0.5)  # Quick check during scrolling
                    else:
                        time.sleep(1)  # Normal wait after clicking
                else:
                    time.sleep(0.5)  # Faster detection cycle
                    
            except Exception as e:
                import traceback
                print(f"Error occurred: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                if self.ui:
                    self.ui.update_status(f"Error: {str(e)}")
                time.sleep(1)
    
    def _start_keyboard_listener(self):
        """Start listening for ESC key press"""
        def on_press(key):
            try:
                if key == keyboard.Key.esc:
                    print("\nESC key pressed - stopping automation...")
                    self.stop_automation()
                    if self.ui:
                        self.ui.update_status("Stopped (ESC key)")
                        self.ui.toggle_button.configure(text="Start")
                        self.ui.is_running = False
                    return False  # Stop listener
            except:
                pass
        
        # Start keyboard listener in non-blocking mode
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()
    
    def _stop_keyboard_listener(self):
        """Stop the keyboard listener"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
    
    def update_settings(self, setting_name, value):
        self.settings[setting_name] = value
        print(f"Updated {setting_name} to {value}")
    
    def run(self):
        self.ui = ControlPanel(
            on_select_region=self.select_region,
            on_start=self.start_automation,
            on_stop=self.stop_automation,
            on_settings_changed=self.update_settings
        )
        self.ui.run()

def main():
    try:
        app = TelegramAutoDownloader()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()