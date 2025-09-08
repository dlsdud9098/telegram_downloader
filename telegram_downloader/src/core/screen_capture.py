import numpy as np
from typing import Tuple, Optional
from mss import mss
from PIL import Image
import cv2


class ScreenCapture:
    """화면 캡처 기능을 제공하는 클래스"""
    
    def __init__(self):
        """스크린 캡처 초기화"""
        self.sct = mss()
        self.monitor_info = self.sct.monitors[0]  # 전체 화면
        
    def capture_region(self, region: Tuple[int, int, int, int]) -> np.ndarray:
        """지정된 영역 캡처
        
        Args:
            region: (x, y, width, height) 형태의 영역
            
        Returns:
            캡처된 이미지 (numpy array)
        """
        x, y, width, height = region
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }
        
        # 화면 캡처
        screenshot = self.sct.grab(monitor)
        
        # numpy 배열로 변환
        img = np.array(screenshot)
        
        # BGRA를 BGR로 변환 (OpenCV 형식)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def capture_full_screen(self) -> np.ndarray:
        """전체 화면 캡처
        
        Returns:
            캡처된 전체 화면 이미지
        """
        screenshot = self.sct.grab(self.sct.monitors[0])
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    
    def get_screen_size(self) -> Tuple[int, int]:
        """화면 크기 반환
        
        Returns:
            (width, height) 튜플
        """
        return (self.monitor_info["width"], self.monitor_info["height"])
    
    def save_screenshot(self, image: np.ndarray, filepath: str) -> None:
        """스크린샷 저장
        
        Args:
            image: 저장할 이미지
            filepath: 저장 경로
        """
        cv2.imwrite(filepath, image)


class RegionSelector:
    """화면 영역 선택 기능을 제공하는 클래스"""
    
    def __init__(self):
        """영역 선택기 초기화"""
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.selected_region = None
        
    def select_region_interactive(self) -> Optional[Tuple[int, int, int, int]]:
        """마우스로 영역 선택 (인터랙티브)
        
        Returns:
            선택된 영역 (x, y, width, height) 또는 None
        """
        # 전체 화면 캡처
        capture = ScreenCapture()
        screenshot = capture.capture_full_screen()
        
        # 창 생성
        cv2.namedWindow("Select Region", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Select Region", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # 마우스 콜백 설정
        cv2.setMouseCallback("Select Region", self._mouse_callback)
        
        # 복사본 생성
        display_img = screenshot.copy()
        
        print("영역을 선택하세요. ESC를 누르면 취소됩니다.")
        
        while True:
            temp_img = display_img.copy()
            
            # 선택 중인 영역 표시
            if self.selecting and self.start_point and self.end_point:
                cv2.rectangle(temp_img, self.start_point, self.end_point, (0, 255, 0), 2)
            
            # 선택 완료된 영역 표시
            if self.selected_region:
                x, y, w, h = self.selected_region
                cv2.rectangle(temp_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(temp_img, "Press ENTER to confirm or ESC to cancel", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("Select Region", temp_img)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                self.selected_region = None
                break
            elif key == 13 and self.selected_region:  # ENTER
                break
        
        cv2.destroyWindow("Select Region")
        return self.selected_region
    
    def _mouse_callback(self, event, x, y, flags, param):
        """마우스 이벤트 콜백"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.end_point = (x, y)
            self.selecting = True
            self.selected_region = None
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selecting:
                self.end_point = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.selecting:
                self.end_point = (x, y)
                self.selecting = False
                
                # 영역 계산
                x1 = min(self.start_point[0], self.end_point[0])
                y1 = min(self.start_point[1], self.end_point[1])
                x2 = max(self.start_point[0], self.end_point[0])
                y2 = max(self.start_point[1], self.end_point[1])
                
                width = x2 - x1
                height = y2 - y1
                
                if width > 10 and height > 10:  # 최소 크기 체크
                    self.selected_region = (x1, y1, width, height)