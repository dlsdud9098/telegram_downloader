import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from dataclasses import dataclass
import threading


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


class ControlPanelTk:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Telegram Auto Downloader")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        self.state = ControlState()
        
        # Callbacks
        self.on_select_region = None
        self.on_start = None
        self.on_stop = None
        self.on_config_change = None
        
        self._create_ui()
        
    def _create_ui(self):
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, text="Telegram Auto Downloader", 
                                font=("Arial", 14, "bold"))
        title_label.pack()
        
        # Control buttons
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        self.select_region_btn = ttk.Button(control_frame, text="Select Region",
                                           command=self._on_select_region)
        self.select_region_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.start_stop_btn = ttk.Button(control_frame, text="Start",
                                        command=self._on_start_stop)
        self.start_stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Statistics
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=50, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Scroll pixels
        scroll_pixels_frame = ttk.Frame(config_frame)
        scroll_pixels_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(scroll_pixels_frame, text="Scroll Pixels:").pack(side=tk.LEFT)
        self.scroll_pixels_var = tk.IntVar(value=100)
        self.scroll_pixels_slider = ttk.Scale(scroll_pixels_frame, from_=50, to=500,
                                             variable=self.scroll_pixels_var,
                                             orient=tk.HORIZONTAL,
                                             command=self._on_scroll_pixels_change)
        self.scroll_pixels_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.scroll_pixels_label = ttk.Label(scroll_pixels_frame, text="100")
        self.scroll_pixels_label.pack(side=tk.LEFT)
        
        # Scroll delay
        scroll_delay_frame = ttk.Frame(config_frame)
        scroll_delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(scroll_delay_frame, text="Scroll Delay (s):").pack(side=tk.LEFT)
        self.scroll_delay_var = tk.DoubleVar(value=0.5)
        self.scroll_delay_slider = ttk.Scale(scroll_delay_frame, from_=0.1, to=2.0,
                                            variable=self.scroll_delay_var,
                                            orient=tk.HORIZONTAL,
                                            command=self._on_scroll_delay_change)
        self.scroll_delay_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.scroll_delay_label = ttk.Label(scroll_delay_frame, text="0.5")
        self.scroll_delay_label.pack(side=tk.LEFT)
        
        # Click delay
        click_delay_frame = ttk.Frame(config_frame)
        click_delay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(click_delay_frame, text="Click Delay (s):").pack(side=tk.LEFT)
        self.click_delay_var = tk.DoubleVar(value=0.5)
        self.click_delay_slider = ttk.Scale(click_delay_frame, from_=0.1, to=2.0,
                                           variable=self.click_delay_var,
                                           orient=tk.HORIZONTAL,
                                           command=self._on_click_delay_change)
        self.click_delay_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.click_delay_label = ttk.Label(click_delay_frame, text="0.5")
        self.click_delay_label.pack(side=tk.LEFT)
        
        # Detection threshold
        threshold_frame = ttk.Frame(config_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(threshold_frame, text="Detection:").pack(side=tk.LEFT)
        self.threshold_var = tk.DoubleVar(value=0.9)
        self.threshold_slider = ttk.Scale(threshold_frame, from_=0.5, to=1.0,
                                         variable=self.threshold_var,
                                         orient=tk.HORIZONTAL,
                                         command=self._on_threshold_change)
        self.threshold_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.threshold_label = ttk.Label(threshold_frame, text="90%")
        self.threshold_label.pack(side=tk.LEFT)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def _on_select_region(self):
        if self.on_select_region:
            # Hide main window temporarily
            self.root.withdraw()
            
            # Run in thread to avoid blocking
            thread = threading.Thread(target=self._do_select_region)
            thread.daemon = True
            thread.start()
    
    def _do_select_region(self):
        try:
            if self.on_select_region:
                self.on_select_region()
        finally:
            # Show window again after selection
            self.root.after(100, self.root.deiconify)
    
    def _on_start_stop(self):
        if self.state.is_running:
            self.stop()
        else:
            self.start()
    
    def _on_scroll_pixels_change(self, value):
        val = int(float(value))
        self.scroll_pixels_label.config(text=str(val))
        self.state.scroll_pixels = val
        self._notify_config_change()
    
    def _on_scroll_delay_change(self, value):
        val = round(float(value), 1)
        self.scroll_delay_label.config(text=str(val))
        self.state.scroll_delay = val
        self._notify_config_change()
    
    def _on_click_delay_change(self, value):
        val = round(float(value), 1)
        self.click_delay_label.config(text=str(val))
        self.state.click_delay = val
        self._notify_config_change()
    
    def _on_threshold_change(self, value):
        val = float(value)
        self.threshold_label.config(text=f"{int(val * 100)}%")
        self.state.detection_threshold = val
        self._notify_config_change()
    
    def _notify_config_change(self):
        if self.on_config_change:
            self.on_config_change(self.state)
    
    def start(self):
        self.state.is_running = True
        self.start_stop_btn.config(text="Stop")
        self.status_label.config(text="Running...")
        
        # Disable configuration during run
        self.select_region_btn.config(state=tk.DISABLED)
        self.scroll_pixels_slider.config(state=tk.DISABLED)
        self.scroll_delay_slider.config(state=tk.DISABLED)
        self.click_delay_slider.config(state=tk.DISABLED)
        self.threshold_slider.config(state=tk.DISABLED)
        
        if self.on_start:
            self.on_start()
    
    def stop(self):
        self.state.is_running = False
        self.start_stop_btn.config(text="Start")
        self.status_label.config(text="Stopped")
        
        # Enable configuration
        self.select_region_btn.config(state=tk.NORMAL)
        self.scroll_pixels_slider.config(state=tk.NORMAL)
        self.scroll_delay_slider.config(state=tk.NORMAL)
        self.click_delay_slider.config(state=tk.NORMAL)
        self.threshold_slider.config(state=tk.NORMAL)
        
        if self.on_stop:
            self.on_stop()
    
    def update_stats(self, stats: dict):
        self.state.stats = stats
        
        text = f"""Total Images: {stats.get('total', 0)}
Not Downloaded: {stats.get('not_downloaded', 0)}
Downloading: {stats.get('downloading', 0)}
Downloaded: {stats.get('downloaded', 0)}
Completion: {stats.get('download_percentage', 0):.1%}"""
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, text)
        self.stats_text.config(state=tk.DISABLED)
    
    def set_status(self, message: str):
        self.status_label.config(text=message)
    
    def set_callbacks(self, on_select_region: Optional[Callable] = None,
                      on_start: Optional[Callable] = None,
                      on_stop: Optional[Callable] = None,
                      on_config_change: Optional[Callable] = None):
        self.on_select_region = on_select_region
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_config_change = on_config_change
    
    def run(self):
        self.root.mainloop()