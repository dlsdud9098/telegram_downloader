#!/usr/bin/env python3

import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.detector import ImageDetector
from src.core.screen_capture import ScreenCapture
from src.core.automation import AutomationController, AutomationConfig
from src.ui.overlay import OverlayWindow
from src.ui.control_panel_tk import ControlPanelTk


class TelegramDownloader:
    def __init__(self):
        self.detector = ImageDetector()
        self.capture = ScreenCapture()
        self.automation = AutomationController()
        self.overlay = None
        self.control_panel = ControlPanelTk()
        self.processing_thread = None
        self.is_processing = False
        
        # Setup callbacks
        self.control_panel.set_callbacks(
            on_select_region=self.select_region,
            on_start=self.start_automation,
            on_stop=self.stop_automation,
            on_config_change=self.update_config
        )
    
    def select_region(self):
        self.control_panel.set_status("Selecting region...")
        
        # Stop any existing overlay
        if self.overlay:
            self.overlay.stop()
            
        # Select region
        region = self.capture.start_region_selection()
        if region:
            self.capture.set_region(
                region["left"], 
                region["top"],
                region["width"], 
                region["height"]
            )
            self.automation.set_region_offset(
                region["left"],
                region["top"]
            )
            
            # Create new overlay
            self.overlay = OverlayWindow(region)
            self.overlay.start()
            
            self.control_panel.set_status(
                f"Region selected: {region['width']}x{region['height']}"
            )
        else:
            self.control_panel.set_status("Region selection cancelled")
    
    def start_automation(self):
        if not self.capture.get_region():
            self.control_panel.set_status("Please select a region first")
            self.control_panel.stop()
            return
        
        self.is_processing = True
        self.automation.start()
        self.capture.start_continuous_capture(fps=5)
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        self.control_panel.set_status("Automation running...")
    
    def stop_automation(self):
        self.is_processing = False
        self.automation.stop()
        self.capture.stop_continuous_capture()
        
        if self.processing_thread and self.processing_thread != threading.current_thread():
            self.processing_thread.join(timeout=1)
        
        self.control_panel.set_status("Automation stopped")
    
    def update_config(self, state):
        self.automation.update_config(
            scroll_pixels=state.scroll_pixels,
            scroll_delay=state.scroll_delay,
            click_delay=state.click_delay,
            detection_threshold=state.detection_threshold
        )
        self.detector.set_threshold(state.detection_threshold)
    
    def _processing_loop(self):
        while self.is_processing:
            try:
                # Get current frame
                frame = self.capture.get_current_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detect images
                detections = self.detector.detect_images(frame)
                
                # Update overlay
                if self.overlay:
                    self.overlay.update_detections(detections)
                
                # Execute automation
                stats = self.automation.execute_automation(detections)
                
                # Update UI stats
                self.control_panel.update_stats(stats)
                
                # Check if we should stop
                if self.automation.should_stop(stats):
                    self.control_panel.stop()
                    self.stop_automation()
                    self.control_panel.set_status(
                        "Stopped: Download threshold reached"
                    )
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
            except Exception as e:
                print(f"Processing error: {e}")
                time.sleep(0.5)
    
    def run(self):
        try:
            # Run control panel (blocks until closed)
            self.control_panel.run()
        finally:
            # Cleanup
            self.stop_automation()
            if self.overlay:
                self.overlay.stop()


def main():
    try:
        app = TelegramDownloader()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
