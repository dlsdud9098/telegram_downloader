import pygame
import threading
import time
from typing import List, Tuple, Optional
import platform
from src.core.detector import Detection, DownloadState


class OverlayWindow:
    def __init__(self, region: dict):
        self.region = region
        self.detections = []
        self.is_running = False
        self.overlay_thread = None
        self.lock = threading.Lock()
        self.opacity = 180
        
        # Colors for different states
        self.colors = {
            DownloadState.NOT_DOWNLOADED: (255, 0, 0),      # Red
            DownloadState.DOWNLOADING: (255, 255, 0),       # Yellow
            DownloadState.DOWNLOADED: (0, 255, 0)           # Green
        }
        
    def start(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.overlay_thread = threading.Thread(target=self._run_overlay)
        self.overlay_thread.daemon = True
        self.overlay_thread.start()
    
    def stop(self):
        self.is_running = False
        if self.overlay_thread:
            self.overlay_thread.join(timeout=1)
    
    def update_detections(self, detections: List[Detection]):
        with self.lock:
            self.detections = detections.copy()
    
    def _run_overlay(self):
        pygame.init()
        
        # Create window at region position
        screen = pygame.display.set_mode(
            (self.region["width"], self.region["height"]),
            pygame.NOFRAME
        )
        pygame.display.set_caption("Telegram Downloader Overlay")
        
        # Platform-specific window setup
        if platform.system() == "Windows":
            self._setup_windows_overlay(screen)
        elif platform.system() == "Linux":
            self._setup_linux_overlay(screen)
        elif platform.system() == "Darwin":  # macOS
            self._setup_macos_overlay(screen)
        
        clock = pygame.time.Clock()
        
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
            
            # Clear screen with transparent background
            screen.fill((0, 0, 0, 0))
            
            # Draw detection boxes
            with self.lock:
                for detection in self.detections:
                    self._draw_detection(screen, detection)
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS for smooth visualization
        
        pygame.quit()
    
    def _draw_detection(self, screen, detection: Detection):
        color = self.colors.get(detection.state, (255, 255, 255))
        x, y, w, h = detection.bbox
        
        # Adjust coordinates relative to region
        x_rel = x
        y_rel = y
        
        # Draw rectangle border
        pygame.draw.rect(screen, color, (x_rel, y_rel, w, h), 3)
        
        # Draw state label
        font = pygame.font.Font(None, 20)
        label = detection.state.value.replace("_", " ").title()
        text = font.render(f"{label} ({detection.confidence:.0%})", 
                          True, color)
        
        # Position label above the box
        label_y = y_rel - 25 if y_rel > 25 else y_rel + h + 5
        screen.blit(text, (x_rel, label_y))
        
        # Draw center point
        cx, cy = detection.center
        pygame.draw.circle(screen, color, (cx, cy), 3)
    
    def _setup_windows_overlay(self, screen):
        try:
            import win32api
            import win32con
            import win32gui
            
            hwnd = pygame.display.get_wm_info()["window"]
            
            # Set window position
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST,
                self.region["left"], self.region["top"],
                self.region["width"], self.region["height"],
                win32con.SWP_NOACTIVATE
            )
            
            # Make window transparent and click-through
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
            
            # Set transparency
            win32gui.SetLayeredWindowAttributes(hwnd, 0, self.opacity, win32con.LWA_ALPHA)
        except ImportError:
            print("pywin32 not installed. Overlay may not work properly on Windows.")
    
    def _setup_linux_overlay(self, screen):
        try:
            import os
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{self.region["left"]},{self.region["top"]}'
            
            # Try to set window properties using xprop if available
            import subprocess
            window_id = pygame.display.get_wm_info()["window"]
            
            # Make window stay on top
            subprocess.run([
                "wmctrl", "-i", "-r", str(window_id),
                "-b", "add,above"
            ], capture_output=True)
            
            # Set window type to utility (makes it float and removes decorations)
            subprocess.run([
                "xprop", "-id", str(window_id),
                "-f", "_NET_WM_WINDOW_TYPE", "32a",
                "-set", "_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_UTILITY"
            ], capture_output=True)
        except Exception as e:
            print(f"Linux overlay setup warning: {e}")
    
    def _setup_macos_overlay(self, screen):
        # macOS specific setup if needed
        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{self.region["left"]},{self.region["top"]}'
    
    def set_opacity(self, opacity: int):
        self.opacity = max(0, min(255, opacity))