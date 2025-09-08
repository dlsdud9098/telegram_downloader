import tkinter as tk
from tkinter import Canvas
import threading


class BorderOverlay:
    """반디캠처럼 선택한 영역 주위에 테두리만 표시하는 오버레이"""
    
    def __init__(self, region: dict):
        self.region = region
        self.is_running = False
        self.overlay_thread = None
        self.root = None
        
    def start(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.overlay_thread = threading.Thread(target=self._run_overlay)
        self.overlay_thread.daemon = True
        self.overlay_thread.start()
    
    def stop(self):
        self.is_running = False
        if self.root:
            self.root.after(0, self._destroy_window)
    
    def _destroy_window(self):
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
    
    def _run_overlay(self):
        self.root = tk.Tk()
        self.root.title("Region Overlay")
        
        # 창 크기와 위치 설정
        x = self.region["left"]
        y = self.region["top"]
        width = self.region["width"]
        height = self.region["height"]
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # 창 스타일 설정 - 테두리만 보이게
        self.root.overrideredirect(True)  # 타이틀바 제거
        self.root.attributes('-topmost', True)  # 항상 위에
        
        # Linux에서 투명 창 만들기
        try:
            self.root.wait_visibility(self.root)
            self.root.attributes('-alpha', 0.3)  # 반투명
        except:
            pass
        
        # Canvas로 테두리 그리기
        canvas = Canvas(self.root, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # 테두리 그리기 (녹색)
        border_width = 3
        canvas.create_rectangle(
            border_width, border_width,
            width - border_width, height - border_width,
            outline='#00FF00', width=border_width, fill=''
        )
        
        # 중앙을 투명하게 만들기 위해 배경을 투명색으로
        self.root.config(bg='black')
        canvas.config(bg='black')
        
        # Linux에서 클릭 통과 설정
        try:
            import subprocess
            import os
            
            # 창 ID 가져오기
            wid = self.root.winfo_id()
            
            # 클릭 통과 속성 설정
            subprocess.run([
                'xprop', '-id', str(wid),
                '-f', '_NET_WM_WINDOW_TYPE', '32a',
                '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DOCK'
            ], capture_output=True)
            
            # 입력 모양 설정 (클릭 통과)
            subprocess.run([
                'xprop', '-id', str(wid),
                '-f', '_NET_WM_BYPASS_COMPOSITOR', '32c',
                '-set', '_NET_WM_BYPASS_COMPOSITOR', '2'
            ], capture_output=True)
        except:
            pass
        
        # 메인 루프
        while self.is_running:
            try:
                self.root.update()
            except:
                break
        
        if self.root:
            self.root.destroy()