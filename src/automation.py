# -*- coding: utf-8 -*-
import pyautogui
import time
from typing import List, Tuple
import platform

class AutomationController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Platform-specific configurations
        system = platform.system()
        if system == 'Darwin':  # macOS
            # macOS may require accessibility permissions
            pass
        elif system == 'Windows':
            # Windows specific settings
            pass
        else:  # Linux
            # Linux may require X11
            pass
        
    def click_positions(self, positions: List[Tuple[int, int]], delay: float = 0.2):
        for x, y in positions:
            pyautogui.click(x, y)
            time.sleep(delay)
    
    def scroll_down(self, amount: int = 3):
        # Platform-specific scroll amounts
        system = platform.system()
        if system == 'Darwin':  # macOS has different scroll behavior
            pyautogui.scroll(-amount * 10)
        else:
            pyautogui.scroll(-amount)
        time.sleep(0.2)  # Shorter delay for continuous scrolling
    
    def perform_automation(self, detection_results: dict, stats: dict, 
                          scroll_amount: int = 3, click_delay: float = 0.2, 
                          scroll_threshold: int = 20) -> bool:
        not_downloaded = detection_results.get('not_downloaded', [])
        
        # First priority: click not downloaded items
        if not_downloaded:
            print(f"Found {len(not_downloaded)} not downloaded images, starting clicks...")
            self.click_positions(not_downloaded, delay=click_delay)
            return True
        
        # Keep scrolling if downloaded percentage is above threshold
        # This will continuously scroll until finding new content
        if stats['downloaded_percentage'] >= scroll_threshold:
            print(f"Download completion {stats['downloaded_percentage']:.1f}%, scrolling...")
            self.scroll_down(amount=scroll_amount)  # Use configurable scroll amount
            return True
                
        return False