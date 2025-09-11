# -*- coding: utf-8 -*-
import customtkinter as ctk
from typing import Optional, Tuple
import mss
from PIL import Image, ImageTk
import platform

class RegionSelector:
    def __init__(self):
        self.selection = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.root = None
        self.canvas = None
        
    def select_region(self) -> Optional[dict]:
        self.selection = None
        
        self.root = ctk.CTk()
        
        # Platform-specific window attributes
        system = platform.system()
        if system == 'Windows':
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-alpha', 0.3)
            self.root.attributes('-topmost', True)
        elif system == 'Darwin':  # macOS
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-alpha', 0.3)
            self.root.attributes('-topmost', True)
        else:  # Linux
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-alpha', 0.3)
            self.root.attributes('-topmost', True)
        
        self.root.configure(bg='black')
        
        self.canvas = ctk.CTkCanvas(self.root, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.configure(bg='black')
        
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.canvas.bind('<Escape>', lambda e: self.root.quit())
        
        info_label = ctk.CTkLabel(
            self.root,
            text="Drag to select region. Press ESC to cancel",
            font=("Arial", 16),
            text_color="white",
            bg_color="black"
        )
        info_label.place(relx=0.5, rely=0.05, anchor='center')
        
        self.root.mainloop()
        
        if self.root:
            self.root.destroy()
        
        return self.selection
    
    def _on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2, fill='', stipple='gray50'
        )
    
    def _on_mouse_drag(self, event):
        if self.rect_id:
            self.canvas.coords(
                self.rect_id,
                self.start_x, self.start_y,
                event.x, event.y
            )
    
    def _on_mouse_up(self, event):
        if self.start_x and self.start_y:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            self.selection = {
                'left': x1,
                'top': y1,
                'width': x2 - x1,
                'height': y2 - y1
            }
            
            self.root.quit()