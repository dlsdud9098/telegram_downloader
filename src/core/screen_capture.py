import mss
import numpy as np
import cv2
from typing import Tuple, Optional, Callable
import threading
import time


class ScreenCapture:
    def __init__(self):
        self.region = None
        self.is_selecting = False
        self.selection_start = None
        self.selection_end = None
        self.capture_thread = None
        self.stop_capture = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def start_region_selection(self, callback: Optional[Callable] = None):
        import pygame
        import sys
        
        pygame.init()
        
        # Create MSS instance in this thread
        with mss.mss() as sct:
            # Get primary monitor info
            monitor = sct.monitors[1]
            screen_width = monitor["width"]
            screen_height = monitor["height"]
            
            # Create fullscreen window without FULLSCREEN flag for better compatibility
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Select Region")
            
            # Set window position to cover full screen
            import os
            os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
            
            # Make window transparent
            import platform
            if platform.system() == "Windows":
                try:
                    import win32api
                    import win32con
                    import win32gui
                    hwnd = pygame.display.get_wm_info()["window"]
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                          win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                                          win32con.WS_EX_LAYERED)
                    win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_COLORKEY)
                except ImportError:
                    pass  # pywin32 not installed
            
            # Capture background
            background = np.array(sct.grab(monitor))
            background = cv2.cvtColor(background, cv2.COLOR_BGRA2RGB)
            background = np.transpose(background, (1, 0, 2))
            background_surface = pygame.surfarray.make_surface(background)
            
            clock = pygame.time.Clock()
            selecting = False
            start_pos = None
            end_pos = None
            
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            selecting = True
                            start_pos = pygame.mouse.get_pos()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1 and selecting:
                            end_pos = pygame.mouse.get_pos()
                            if start_pos and end_pos:
                                x1, y1 = min(start_pos[0], end_pos[0]), min(start_pos[1], end_pos[1])
                                x2, y2 = max(start_pos[0], end_pos[0]), max(start_pos[1], end_pos[1])
                                
                                if x2 - x1 > 10 and y2 - y1 > 10:  # Minimum size
                                    self.region = {
                                        "top": y1,
                                        "left": x1,
                                        "width": x2 - x1,
                                        "height": y2 - y1
                                    }
                                    if callback:
                                        callback(self.region)
                                    running = False
                            selecting = False
                
                # Draw
                screen.fill((0, 0, 0))
                screen.blit(background_surface, (0, 0))
                
                # Draw selection rectangle
                if selecting and start_pos:
                    current_pos = pygame.mouse.get_pos()
                    x1, y1 = min(start_pos[0], current_pos[0]), min(start_pos[1], current_pos[1])
                    x2, y2 = max(start_pos[0], current_pos[0]), max(start_pos[1], current_pos[1])
                    
                    # Draw semi-transparent overlay
                    overlay = pygame.Surface((screen_width, screen_height))
                    overlay.set_alpha(128)
                    overlay.fill((0, 0, 0))
                    screen.blit(overlay, (0, 0))
                    
                    # Clear selection area
                    if x2 - x1 > 0 and y2 - y1 > 0:
                        selection_area = background_surface.subsurface((x1, y1, x2-x1, y2-y1))
                        screen.blit(selection_area, (x1, y1))
                        
                        # Draw border
                        pygame.draw.rect(screen, (0, 255, 0), (x1, y1, x2-x1, y2-y1), 2)
                
                pygame.display.flip()
                clock.tick(60)
            
            pygame.quit()
        return self.region
    
    def capture_region(self) -> Optional[np.ndarray]:
        if not self.region:
            return None
        
        try:
            # Create MSS instance for this thread
            with mss.mss() as sct:
                screenshot = sct.grab(self.region)
                img = np.array(screenshot)
                # Convert BGRA to BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return img
        except Exception as e:
            print(f"Capture error: {e}")
            return None
    
    def start_continuous_capture(self, fps: int = 5):
        if self.capture_thread and self.capture_thread.is_alive():
            return
        
        self.stop_capture = False
        self.capture_thread = threading.Thread(target=self._capture_loop, args=(fps,))
        self.capture_thread.start()
    
    def stop_continuous_capture(self):
        self.stop_capture = True
        if self.capture_thread:
            self.capture_thread.join()
    
    def _capture_loop(self, fps: int):
        interval = 1.0 / fps
        while not self.stop_capture:
            start_time = time.time()
            
            frame = self.capture_region()
            if frame is not None:
                with self.frame_lock:
                    self.current_frame = frame
            
            elapsed = time.time() - start_time
            if elapsed < interval:
                time.sleep(interval - elapsed)
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_region(self) -> Optional[dict]:
        return self.region
    
    def set_region(self, x: int, y: int, width: int, height: int):
        self.region = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }