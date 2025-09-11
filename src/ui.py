# -*- coding: utf-8 -*-
import customtkinter as ctk
from threading import Thread, Event
import time
from typing import Optional

class ControlPanel:
    def __init__(self, on_select_region, on_start, on_stop, on_settings_changed=None):
        self.on_select_region = on_select_region
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_settings_changed = on_settings_changed
        
        self.root = None
        self.is_running = False
        self.status_label = None
        self.stats_label = None
        self.region_label = None
        self.selected_region = None
        
        # Settings sliders
        self.scroll_amount_slider = None
        self.click_delay_slider = None
        self.scroll_threshold_slider = None
        self.scroll_amount_label = None
        self.click_delay_label = None
        self.scroll_threshold_label = None
        
    def create_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Telegram Auto Downloader")
        self.root.geometry("450x700")
        self.root.resizable(False, False)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Telegram Auto Downloader",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        region_frame = ctk.CTkFrame(main_frame)
        region_frame.pack(fill="x", padx=10, pady=10)
        
        self.region_label = ctk.CTkLabel(
            region_frame,
            text="Region: Not selected",
            font=ctk.CTkFont(size=12)
        )
        self.region_label.pack(pady=5)
        
        select_btn = ctk.CTkButton(
            region_frame,
            text="Select Region",
            command=self._on_select_region,
            width=200,
            height=40
        )
        select_btn.pack(pady=5)
        
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="Start",
            command=self._on_start,
            width=150,
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="Stop",
            command=self._on_stop,
            width=150,
            height=40,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=5, expand=True, fill="x")
        
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="Status",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_title.pack(pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Waiting...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        self.stats_label = ctk.CTkLabel(
            status_frame,
            text="Statistics:\nTotal: 0\nNot Downloaded: 0\nDownloading: 0\nDownloaded: 0\nCompletion: 0%",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.stats_label.pack(pady=10)
        
        # Settings Frame
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_title.pack(pady=5)
        
        # Scroll Amount
        scroll_amount_frame = ctk.CTkFrame(settings_frame)
        scroll_amount_frame.pack(fill="x", padx=10, pady=5)
        
        self.scroll_amount_label = ctk.CTkLabel(
            scroll_amount_frame,
            text="Scroll Amount: 3",
            font=ctk.CTkFont(size=11)
        )
        self.scroll_amount_label.pack(anchor="w")
        
        self.scroll_amount_slider = ctk.CTkSlider(
            scroll_amount_frame,
            from_=1,
            to=20,
            number_of_steps=19,
            command=self._on_scroll_amount_changed
        )
        self.scroll_amount_slider.set(3)
        self.scroll_amount_slider.pack(fill="x", pady=2)
        
        # Click Delay
        click_delay_frame = ctk.CTkFrame(settings_frame)
        click_delay_frame.pack(fill="x", padx=10, pady=5)
        
        self.click_delay_label = ctk.CTkLabel(
            click_delay_frame,
            text="Click Delay: 0.2s",
            font=ctk.CTkFont(size=11)
        )
        self.click_delay_label.pack(anchor="w")
        
        self.click_delay_slider = ctk.CTkSlider(
            click_delay_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            command=self._on_click_delay_changed
        )
        self.click_delay_slider.set(0.2)
        self.click_delay_slider.pack(fill="x", pady=2)
        
        # Scroll Threshold
        scroll_threshold_frame = ctk.CTkFrame(settings_frame)
        scroll_threshold_frame.pack(fill="x", padx=10, pady=5)
        
        self.scroll_threshold_label = ctk.CTkLabel(
            scroll_threshold_frame,
            text="Scroll Threshold: 20%",
            font=ctk.CTkFont(size=11)
        )
        self.scroll_threshold_label.pack(anchor="w")
        
        self.scroll_threshold_slider = ctk.CTkSlider(
            scroll_threshold_frame,
            from_=10,
            to=90,
            number_of_steps=8,
            command=self._on_scroll_threshold_changed
        )
        self.scroll_threshold_slider.set(20)
        self.scroll_threshold_slider.pack(fill="x", pady=2)
        
        instruction_frame = ctk.CTkFrame(main_frame)
        instruction_frame.pack(fill="x", padx=10, pady=10)
        
        instructions = ctk.CTkLabel(
            instruction_frame,
            text="Instructions:\n1. Use Select Region button to define detection area\n2. Open Telegram app and navigate to channel\n3. Click Start button\n4. Automatically clicks not downloaded files and scrolls",
            font=ctk.CTkFont(size=10),
            justify="left",
            text_color="gray"
        )
        instructions.pack(pady=5)
        
    def _on_select_region(self):
        self.root.withdraw()
        region = self.on_select_region()
        self.root.deiconify()
        
        if region:
            self.selected_region = region
            self.region_label.configure(
                text=f"Region: {region['width']}x{region['height']} at ({region['left']}, {region['top']})"
            )
            # Warn if region is too small
            if region['width'] < 100 or region['height'] < 100:
                self.update_status("Warning: Region may be too small for detection")
            else:
                self.update_status("Region selected")
    
    def _on_start(self):
        if not self.selected_region:
            self.update_status("Please select a region first!")
            return
            
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.update_status("Starting automation...")
        self.on_start(self.selected_region)
    
    def _on_stop(self):
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_status("Automation stopped")
        self.on_stop()
    
    def update_status(self, message: str):
        if self.status_label:
            self.status_label.configure(text=message)
    
    def update_stats(self, stats: dict):
        if self.stats_label:
            text = f"Statistics:\n"
            text += f"Total: {stats.get('total', 0)}\n"
            text += f"Not Downloaded: {stats.get('not_downloaded', 0)}\n"
            text += f"Downloading: {stats.get('downloading', 0)}\n"
            text += f"Downloaded: {stats.get('downloaded', 0)}\n"
            text += f"Completion: {stats.get('downloaded_percentage', 0):.1f}%"
            self.stats_label.configure(text=text)
    
    def _on_scroll_amount_changed(self, value):
        self.scroll_amount_label.configure(text=f"Scroll Amount: {int(value)}")
        if self.on_settings_changed:
            self.on_settings_changed('scroll_amount', int(value))
    
    def _on_click_delay_changed(self, value):
        self.click_delay_label.configure(text=f"Click Delay: {value:.1f}s")
        if self.on_settings_changed:
            self.on_settings_changed('click_delay', value)
    
    def _on_scroll_threshold_changed(self, value):
        self.scroll_threshold_label.configure(text=f"Scroll Threshold: {int(value)}%")
        if self.on_settings_changed:
            self.on_settings_changed('scroll_threshold', int(value))
    
    def get_settings(self):
        return {
            'scroll_amount': int(self.scroll_amount_slider.get()) if self.scroll_amount_slider else 3,
            'click_delay': self.click_delay_slider.get() if self.click_delay_slider else 0.2,
            'scroll_threshold': int(self.scroll_threshold_slider.get()) if self.scroll_threshold_slider else 20
        }
    
    def run(self):
        self.create_ui()
        self.root.mainloop()