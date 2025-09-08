import pygame
import pygame_gui
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class ControlState:
    is_running: bool = False
    scroll_pixels: int = 100
    scroll_delay: float = 0.5
    click_delay: float = 0.5
    detection_threshold: float = 0.9
    stats: dict = None
    
    def __post_init__(self):
        if self.stats is None:
            self.stats = {
                "total": 0,
                "not_downloaded": 0,
                "downloading": 0,
                "downloaded": 0,
                "download_percentage": 0.0
            }


class ControlPanel:
    def __init__(self, width: int = 400, height: int = 500):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Telegram Downloader Control")
        
        self.manager = pygame_gui.UIManager((width, height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = ControlState()
        
        # Callbacks
        self.on_select_region = None
        self.on_start = None
        self.on_stop = None
        self.on_config_change = None
        
        self._create_ui()
    
    def _create_ui(self):
        y_offset = 10
        
        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 380, 30),
            text="Telegram Auto Downloader",
            manager=self.manager
        )
        y_offset += 40
        
        # Region selection button
        self.select_region_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, 180, 40),
            text="Select Region",
            manager=self.manager
        )
        
        # Start/Stop button
        self.start_stop_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(210, y_offset, 180, 40),
            text="Start",
            manager=self.manager
        )
        y_offset += 50
        
        # Statistics
        self.stats_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 380, 20),
            text="Statistics",
            manager=self.manager
        )
        y_offset += 25
        
        self.stats_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, y_offset, 380, 100),
            html_text="No data yet...",
            manager=self.manager
        )
        y_offset += 110
        
        # Configuration
        self.config_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 380, 20),
            text="Configuration",
            manager=self.manager
        )
        y_offset += 30
        
        # Scroll pixels
        self.scroll_pixels_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 20),
            text="Scroll Pixels:",
            manager=self.manager
        )
        self.scroll_pixels_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(170, y_offset, 150, 20),
            start_value=100,
            value_range=(50, 500),
            manager=self.manager
        )
        self.scroll_pixels_value = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(330, y_offset, 60, 20),
            text="100",
            manager=self.manager
        )
        y_offset += 30
        
        # Scroll delay
        self.scroll_delay_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 20),
            text="Scroll Delay (s):",
            manager=self.manager
        )
        self.scroll_delay_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(170, y_offset, 150, 20),
            start_value=0.5,
            value_range=(0.1, 2.0),
            manager=self.manager
        )
        self.scroll_delay_value = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(330, y_offset, 60, 20),
            text="0.5",
            manager=self.manager
        )
        y_offset += 30
        
        # Click delay
        self.click_delay_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 20),
            text="Click Delay (s):",
            manager=self.manager
        )
        self.click_delay_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(170, y_offset, 150, 20),
            start_value=0.5,
            value_range=(0.1, 2.0),
            manager=self.manager
        )
        self.click_delay_value = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(330, y_offset, 60, 20),
            text="0.5",
            manager=self.manager
        )
        y_offset += 30
        
        # Detection threshold
        self.threshold_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, 150, 20),
            text="Detection Threshold:",
            manager=self.manager
        )
        self.threshold_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(170, y_offset, 150, 20),
            start_value=0.9,
            value_range=(0.5, 1.0),
            manager=self.manager
        )
        self.threshold_value = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(330, y_offset, 60, 20),
            text="90%",
            manager=self.manager
        )
        y_offset += 40
        
        # Status bar
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, self.height - 30, 380, 20),
            text="Ready",
            manager=self.manager
        )
    
    def run(self):
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.select_region_btn:
                        if self.on_select_region:
                            self.on_select_region()
                    elif event.ui_element == self.start_stop_btn:
                        if self.state.is_running:
                            self.stop()
                        else:
                            self.start()
                
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self._handle_slider_change(event.ui_element)
                
                self.manager.process_events(event)
            
            self.manager.update(time_delta)
            
            self.screen.fill((30, 30, 30))
            self.manager.draw_ui(self.screen)
            
            pygame.display.flip()
    
    def _handle_slider_change(self, slider):
        if slider == self.scroll_pixels_slider:
            value = int(slider.get_current_value())
            self.scroll_pixels_value.set_text(str(value))
            self.state.scroll_pixels = value
        elif slider == self.scroll_delay_slider:
            value = round(slider.get_current_value(), 1)
            self.scroll_delay_value.set_text(str(value))
            self.state.scroll_delay = value
        elif slider == self.click_delay_slider:
            value = round(slider.get_current_value(), 1)
            self.click_delay_value.set_text(str(value))
            self.state.click_delay = value
        elif slider == self.threshold_slider:
            value = slider.get_current_value()
            self.threshold_value.set_text(f"{int(value * 100)}%")
            self.state.detection_threshold = value
        
        if self.on_config_change:
            self.on_config_change(self.state)
    
    def start(self):
        self.state.is_running = True
        self.start_stop_btn.set_text("Stop")
        self.status_label.set_text("Running...")
        
        # Disable configuration during run
        self.select_region_btn.disable()
        self.scroll_pixels_slider.disable()
        self.scroll_delay_slider.disable()
        self.click_delay_slider.disable()
        self.threshold_slider.disable()
        
        if self.on_start:
            self.on_start()
    
    def stop(self):
        self.state.is_running = False
        self.start_stop_btn.set_text("Start")
        self.status_label.set_text("Stopped")
        
        # Enable configuration
        self.select_region_btn.enable()
        self.scroll_pixels_slider.enable()
        self.scroll_delay_slider.enable()
        self.click_delay_slider.enable()
        self.threshold_slider.enable()
        
        if self.on_stop:
            self.on_stop()
    
    def update_stats(self, stats: dict):
        self.state.stats = stats
        
        text = f"""
        <b>Total Images:</b> {stats.get('total', 0)}<br>
        <b>Not Downloaded:</b> {stats.get('not_downloaded', 0)}<br>
        <b>Downloading:</b> {stats.get('downloading', 0)}<br>
        <b>Downloaded:</b> {stats.get('downloaded', 0)}<br>
        <b>Completion:</b> {stats.get('download_percentage', 0):.1%}
        """
        
        self.stats_text.set_text(text)
    
    def set_status(self, message: str):
        self.status_label.set_text(message)
    
    def set_callbacks(self, on_select_region: Optional[Callable] = None,
                      on_start: Optional[Callable] = None,
                      on_stop: Optional[Callable] = None,
                      on_config_change: Optional[Callable] = None):
        self.on_select_region = on_select_region
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_config_change = on_config_change