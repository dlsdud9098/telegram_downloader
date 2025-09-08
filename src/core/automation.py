import pyautogui
import time
import threading
from typing import List, Optional, Tuple
from dataclasses import dataclass
from src.core.detector import Detection, DownloadState


@dataclass
class AutomationConfig:
    scroll_pixels: int = 100
    scroll_delay: float = 0.5
    click_delay: float = 0.5
    detection_threshold: float = 0.9
    download_complete_threshold: float = 0.8  # 80% downloaded to scroll
    download_stop_threshold: float = 0.2      # 20% downloaded to stop


class AutomationController:
    def __init__(self, config: Optional[AutomationConfig] = None):
        self.config = config or AutomationConfig()
        self.is_running = False
        self.automation_thread = None
        self.last_click_time = 0
        self.last_scroll_time = 0
        self.region_offset = (0, 0)  # Offset from screen origin
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def set_region_offset(self, x: int, y: int):
        self.region_offset = (x, y)
    
    def start(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.automation_thread = threading.Thread(target=self._automation_loop)
        self.automation_thread.daemon = True
        self.automation_thread.start()
    
    def stop(self):
        self.is_running = False
        if self.automation_thread:
            self.automation_thread.join(timeout=1)
    
    def process_detections(self, detections: List[Detection]) -> dict:
        stats = {
            "total": len(detections),
            "not_downloaded": 0,
            "downloading": 0,
            "downloaded": 0,
            "download_percentage": 0.0
        }
        
        if not detections:
            return stats
        
        # Count by state
        for detection in detections:
            if detection.state == DownloadState.NOT_DOWNLOADED:
                stats["not_downloaded"] += 1
            elif detection.state == DownloadState.DOWNLOADING:
                stats["downloading"] += 1
            elif detection.state == DownloadState.DOWNLOADED:
                stats["downloaded"] += 1
        
        # Calculate download percentage
        if stats["total"] > 0:
            stats["download_percentage"] = stats["downloaded"] / stats["total"]
        
        return stats
    
    def should_scroll(self, stats: dict) -> bool:
        if stats["total"] == 0:
            return False
        
        # Scroll if more than 80% are downloaded
        return stats["download_percentage"] >= self.config.download_complete_threshold
    
    def should_stop(self, stats: dict) -> bool:
        if stats["total"] == 0:
            return True
        
        # Stop if less than 20% are downloaded
        return stats["download_percentage"] < self.config.download_stop_threshold
    
    def click_not_downloaded(self, detections: List[Detection]):
        current_time = time.time()
        
        # Check click delay
        if current_time - self.last_click_time < self.config.click_delay:
            return
        
        # Find not downloaded images
        not_downloaded = [d for d in detections 
                         if d.state == DownloadState.NOT_DOWNLOADED]
        
        if not not_downloaded:
            print("No 'not downloaded' images found")
            return
        
        print(f"Found {len(not_downloaded)} not downloaded images")
        
        # Sort by position (top to bottom, left to right)
        not_downloaded.sort(key=lambda d: (d.center[1], d.center[0]))
        
        # Click the first one
        detection = not_downloaded[0]
        click_x = self.region_offset[0] + detection.center[0]
        click_y = self.region_offset[1] + detection.center[1]
        
        try:
            print(f"Moving to ({click_x}, {click_y}) and clicking...")
            # Move to position and click
            pyautogui.moveTo(click_x, click_y, duration=0.1)
            time.sleep(0.1)  # Small delay before click
            pyautogui.click()
            self.last_click_time = current_time
            print(f"Successfully clicked at ({click_x}, {click_y})")
        except Exception as e:
            print(f"Click error: {e}")
            import traceback
            traceback.print_exc()
    
    def scroll_down(self):
        current_time = time.time()
        
        # Check scroll delay
        if current_time - self.last_scroll_time < self.config.scroll_delay:
            return
        
        try:
            # Scroll down
            pyautogui.scroll(-self.config.scroll_pixels)
            self.last_scroll_time = current_time
            print(f"Scrolled down {self.config.scroll_pixels} pixels")
        except Exception as e:
            print(f"Scroll error: {e}")
    
    def execute_automation(self, detections: List[Detection]) -> dict:
        stats = self.process_detections(detections)
        
        if self.should_stop(stats):
            print("Stopping: Download percentage below threshold")
            return stats
        
        if self.should_scroll(stats):
            self.scroll_down()
        else:
            self.click_not_downloaded(detections)
        
        return stats
    
    def _automation_loop(self):
        # This is a placeholder for integration with the main app
        # The actual loop will be handled by the main application
        while self.is_running:
            time.sleep(0.1)
    
    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)