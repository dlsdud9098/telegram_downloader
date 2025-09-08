import pyautogui
import time
from typing import List, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import threading
from queue import Queue

from .image_detector import ImageDetector, ImageStatus, DetectionResult
from .screen_capture import ScreenCapture


class AutomationState(Enum):
    """자동화 상태"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class AutomationConfig:
    """자동화 설정"""
    scroll_speed: int = 5  # 스크롤 속도
    scroll_pause: float = 0.5  # 스크롤 후 대기 시간
    click_pause: float = 0.3  # 클릭 후 대기 시간
    detection_interval: float = 1.0  # 감지 주기
    completion_threshold_high: float = 0.9  # 스크롤 시작 임계값
    completion_threshold_low: float = 0.3  # 스크롤 정지 임계값
    safe_mode: bool = True  # 안전 모드 (pyautogui fail-safe)


class DownloadAutomation:
    """다운로드 자동화 클래스"""
    
    def __init__(self, detector: ImageDetector, config: AutomationConfig = None):
        """
        Args:
            detector: 이미지 감지기
            config: 자동화 설정
        """
        self.detector = detector
        self.config = config or AutomationConfig()
        self.capture = ScreenCapture()
        
        self.state = AutomationState.IDLE
        self.region: Optional[Tuple[int, int, int, int]] = None
        self.worker_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        
        # 콜백 함수들
        self.on_state_change: Optional[Callable] = None
        self.on_detection: Optional[Callable] = None
        self.on_scroll: Optional[Callable] = None
        self.on_click: Optional[Callable] = None
        self.on_completion: Optional[Callable] = None
        
        # PyAutoGUI 설정
        pyautogui.FAILSAFE = self.config.safe_mode
        pyautogui.PAUSE = 0.1
        
    def set_region(self, region: Tuple[int, int, int, int]) -> None:
        """감지할 영역 설정
        
        Args:
            region: (x, y, width, height) 형태의 영역
        """
        self.region = region
        
    def start(self) -> bool:
        """자동화 시작
        
        Returns:
            시작 성공 여부
        """
        if not self.region:
            print("영역이 설정되지 않았습니다.")
            return False
            
        if self.state == AutomationState.RUNNING:
            print("이미 실행 중입니다.")
            return False
            
        self.stop_event.clear()
        self.pause_event.set()  # 시작 시 일시정지 해제
        
        self.worker_thread = threading.Thread(target=self._automation_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        self._set_state(AutomationState.RUNNING)
        return True
        
    def pause(self) -> None:
        """자동화 일시정지"""
        if self.state == AutomationState.RUNNING:
            self.pause_event.clear()
            self._set_state(AutomationState.PAUSED)
            
    def resume(self) -> None:
        """자동화 재개"""
        if self.state == AutomationState.PAUSED:
            self.pause_event.set()
            self._set_state(AutomationState.RUNNING)
            
    def stop(self) -> None:
        """자동화 정지"""
        self.stop_event.set()
        self.pause_event.set()  # 일시정지 상태라면 해제
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
            
        self._set_state(AutomationState.STOPPED)
        
    def _set_state(self, state: AutomationState) -> None:
        """상태 변경
        
        Args:
            state: 새로운 상태
        """
        self.state = state
        if self.on_state_change:
            self.on_state_change(state)
            
    def _automation_loop(self) -> None:
        """자동화 메인 루프"""
        reached_bottom = False
        
        while not self.stop_event.is_set():
            # 일시정지 상태 체크
            self.pause_event.wait()
            
            if self.stop_event.is_set():
                break
                
            try:
                # 화면 캡처
                screen_img = self.capture.capture_region(self.region)
                
                # 이미지 감지
                detections = self.detector.detect_all(screen_img)
                
                if self.on_detection:
                    self.on_detection(detections)
                
                # 다운로드 전 이미지 클릭
                before_downloads = detections.get(ImageStatus.BEFORE_DOWNLOAD, [])
                for detection in before_downloads:
                    self._click_image(detection)
                    time.sleep(self.config.click_pause)
                
                # 완료 비율 계산
                completion_ratio = self.detector.calculate_completion_ratio(detections)
                
                # 스크롤 로직
                if completion_ratio >= self.config.completion_threshold_high:
                    # 90% 이상 완료 시 스크롤
                    self._scroll_down()
                    reached_bottom = False
                    
                elif completion_ratio < self.config.completion_threshold_low:
                    # 30% 미만일 때
                    if not reached_bottom:
                        # 아직 하단이 아니면 대기
                        time.sleep(self.config.detection_interval)
                    else:
                        # 하단 도달 시 완료
                        if self.on_completion:
                            self.on_completion()
                        break
                        
                else:
                    # 30% ~ 90% 사이: 대기
                    time.sleep(self.config.detection_interval)
                    
                # 스크롤이 더 이상 안되는지 체크 (하단 도달)
                if not self._can_scroll_more():
                    reached_bottom = True
                    
            except Exception as e:
                print(f"자동화 루프 오류: {e}")
                time.sleep(self.config.detection_interval)
                
        self._set_state(AutomationState.IDLE)
        
    def _click_image(self, detection: DetectionResult) -> None:
        """이미지 클릭
        
        Args:
            detection: 감지 결과
        """
        # 영역 좌표를 화면 좌표로 변환
        screen_x = self.region[0] + detection.position[0]
        screen_y = self.region[1] + detection.position[1]
        
        pyautogui.click(screen_x, screen_y)
        
        if self.on_click:
            self.on_click((screen_x, screen_y))
            
    def _scroll_down(self) -> None:
        """아래로 스크롤"""
        # 영역 중앙으로 마우스 이동
        center_x = self.region[0] + self.region[2] // 2
        center_y = self.region[1] + self.region[3] // 2
        
        pyautogui.moveTo(center_x, center_y)
        pyautogui.scroll(-self.config.scroll_speed)
        
        if self.on_scroll:
            self.on_scroll(self.config.scroll_speed)
            
        time.sleep(self.config.scroll_pause)
        
    def _can_scroll_more(self) -> bool:
        """더 스크롤할 수 있는지 확인
        
        Returns:
            스크롤 가능 여부
        """
        # 스크롤 전 화면 캡처
        before_img = self.capture.capture_region(self.region)
        
        # 작은 스크롤 시도
        center_x = self.region[0] + self.region[2] // 2
        center_y = self.region[1] + self.region[3] // 2
        pyautogui.moveTo(center_x, center_y)
        pyautogui.scroll(-1)
        
        time.sleep(0.2)
        
        # 스크롤 후 화면 캡처
        after_img = self.capture.capture_region(self.region)
        
        # 화면 변화 감지
        import cv2
        diff = cv2.absdiff(before_img, after_img)
        change_amount = diff.mean()
        
        # 변화가 거의 없으면 하단 도달
        return change_amount > 1.0