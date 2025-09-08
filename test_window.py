#!/usr/bin/env python3

import tkinter as tk
from tkinter import Canvas
import random

class TestWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Window for Telegram Downloader")
        self.root.geometry("600x400")
        
        # Canvas for drawing test images
        self.canvas = Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create test circles that look like our test images
        self.create_test_images()
        
        # Button to refresh
        refresh_btn = tk.Button(self.root, text="Refresh Images", 
                               command=self.create_test_images)
        refresh_btn.pack(pady=10)
        
        self.root.mainloop()
    
    def create_test_images(self):
        self.canvas.delete("all")
        
        # Create random circles representing download states
        for _ in range(5):
            x = random.randint(50, 550)
            y = random.randint(50, 350)
            
            # Randomly choose a state
            state = random.choice(["not_download", "downloading", "downloaded"])
            
            if state == "not_download":
                color = "red"
            elif state == "downloading":
                color = "yellow"
            else:
                color = "green"
            
            # Draw circle (like our test images)
            self.canvas.create_oval(x-24, y-24, x+24, y+24, 
                                   fill=color, outline="gray", width=2)
            
            # Add click handler
            circle_id = self.canvas.find_closest(x, y)
            self.canvas.tag_bind(circle_id, "<Button-1>", 
                               lambda e, c=color: self.on_click(e, c))
    
    def on_click(self, event, color):
        print(f"Clicked on {color} circle at ({event.x}, {event.y})")
        # Change red circles to yellow when clicked
        if color == "red":
            item = self.canvas.find_closest(event.x, event.y)
            self.canvas.itemconfig(item, fill="yellow")

if __name__ == "__main__":
    TestWindow()