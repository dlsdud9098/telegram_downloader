from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QTextEdit, QFileDialog,
    QMessageBox, QProgressBar, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QPixmap, QImage, QPalette, QColor
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, List, Optional

from ..core.image_detector import ImageDetector, ImageStatus, DetectionResult
from ..core.screen_capture import ScreenCapture, RegionSelector
from ..core.automation import DownloadAutomation, AutomationConfig, AutomationState


class DetectionThread(QThread):
    """감지 작업을 위한 스레드"""
    detection_update = Signal(dict)
    log_message = Signal(str)
    
    def __init__(self, automation: DownloadAutomation):
        super().__init__()
        self.automation = automation
        
    def run(self):
        """스레드 실행"""
        # 자동화 콜백 설정
        self.automation.on_detection = self._on_detection
        self.automation.on_click = self._on_click
        self.automation.on_scroll = self._on_scroll
        self.automation.on_completion = self._on_completion
        
    def _on_detection(self, detections: Dict):
        self.detection_update.emit(detections)
        
    def _on_click(self, position):
        self.log_message.emit(f"클릭: {position}")
        
    def _on_scroll(self, amount):
        self.log_message.emit(f"스크롤: {amount}")
        
    def _on_completion(self):
        self.log_message.emit("자동화 완료!")


class MainWindow(QMainWindow):
    """메인 애플리케이션 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.detector = ImageDetector()
        self.automation = None
        self.detection_thread = None
        self.selected_region = None
        self.template_paths = {
            ImageStatus.BEFORE_DOWNLOAD: None,
            ImageStatus.DOWNLOADING: None,
            ImageStatus.COMPLETED: None
        }
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("Telegram Downloader Automation")
        self.setGeometry(100, 100, 900, 700)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 템플릿 설정 그룹
        template_group = self.create_template_group()
        main_layout.addWidget(template_group)
        
        # 영역 선택 그룹
        region_group = self.create_region_group()
        main_layout.addWidget(region_group)
        
        # 설정 그룹
        config_group = self.create_config_group()
        main_layout.addWidget(config_group)
        
        # 컨트롤 그룹
        control_group = self.create_control_group()
        main_layout.addWidget(control_group)
        
        # 상태 표시 그룹
        status_group = self.create_status_group()
        main_layout.addWidget(status_group)
        
        # 로그 그룹
        log_group = self.create_log_group()
        main_layout.addWidget(log_group)
        
    def create_template_group(self) -> QGroupBox:
        """템플릿 설정 그룹 생성"""
        group = QGroupBox("템플릿 이미지 설정")
        layout = QVBoxLayout()
        
        # 다운로드 전 이미지
        before_layout = QHBoxLayout()
        before_layout.addWidget(QLabel("다운로드 전:"))
        self.before_label = QLabel("선택되지 않음")
        self.before_label.setMinimumWidth(200)
        before_layout.addWidget(self.before_label)
        self.before_btn = QPushButton("선택...")
        self.before_btn.clicked.connect(lambda: self.select_template(ImageStatus.BEFORE_DOWNLOAD))
        before_layout.addWidget(self.before_btn)
        layout.addLayout(before_layout)
        
        # 다운로드 중 이미지
        downloading_layout = QHBoxLayout()
        downloading_layout.addWidget(QLabel("다운로드 중:"))
        self.downloading_label = QLabel("선택되지 않음")
        self.downloading_label.setMinimumWidth(200)
        downloading_layout.addWidget(self.downloading_label)
        self.downloading_btn = QPushButton("선택...")
        self.downloading_btn.clicked.connect(lambda: self.select_template(ImageStatus.DOWNLOADING))
        downloading_layout.addWidget(self.downloading_btn)
        layout.addLayout(downloading_layout)
        
        # 다운로드 완료 이미지
        completed_layout = QHBoxLayout()
        completed_layout.addWidget(QLabel("다운로드 완료:"))
        self.completed_label = QLabel("선택되지 않음")
        self.completed_label.setMinimumWidth(200)
        completed_layout.addWidget(self.completed_label)
        self.completed_btn = QPushButton("선택...")
        self.completed_btn.clicked.connect(lambda: self.select_template(ImageStatus.COMPLETED))
        completed_layout.addWidget(self.completed_btn)
        layout.addLayout(completed_layout)
        
        group.setLayout(layout)
        return group
        
    def create_region_group(self) -> QGroupBox:
        """영역 선택 그룹 생성"""
        group = QGroupBox("감지 영역 설정")
        layout = QHBoxLayout()
        
        self.region_label = QLabel("영역이 선택되지 않음")
        layout.addWidget(self.region_label)
        
        self.select_region_btn = QPushButton("영역 선택")
        self.select_region_btn.clicked.connect(self.select_region)
        layout.addWidget(self.select_region_btn)
        
        group.setLayout(layout)
        return group
        
    def create_config_group(self) -> QGroupBox:
        """설정 그룹 생성"""
        group = QGroupBox("자동화 설정")
        layout = QVBoxLayout()
        
        # 스크롤 설정
        scroll_layout = QHBoxLayout()
        scroll_layout.addWidget(QLabel("스크롤 속도:"))
        self.scroll_speed_spin = QSpinBox()
        self.scroll_speed_spin.setRange(1, 20)
        self.scroll_speed_spin.setValue(5)
        scroll_layout.addWidget(self.scroll_speed_spin)
        
        scroll_layout.addWidget(QLabel("스크롤 대기(초):"))
        self.scroll_pause_spin = QDoubleSpinBox()
        self.scroll_pause_spin.setRange(0.1, 5.0)
        self.scroll_pause_spin.setValue(0.5)
        self.scroll_pause_spin.setSingleStep(0.1)
        scroll_layout.addWidget(self.scroll_pause_spin)
        layout.addLayout(scroll_layout)
        
        # 임계값 설정
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("완료 임계값(상한 %):"))
        self.high_threshold_spin = QSpinBox()
        self.high_threshold_spin.setRange(50, 100)
        self.high_threshold_spin.setValue(90)
        threshold_layout.addWidget(self.high_threshold_spin)
        
        threshold_layout.addWidget(QLabel("완료 임계값(하한 %):"))
        self.low_threshold_spin = QSpinBox()
        self.low_threshold_spin.setRange(10, 50)
        self.low_threshold_spin.setValue(30)
        threshold_layout.addWidget(self.low_threshold_spin)
        layout.addLayout(threshold_layout)
        
        # 기타 설정
        other_layout = QHBoxLayout()
        other_layout.addWidget(QLabel("감지 주기(초):"))
        self.detection_interval_spin = QDoubleSpinBox()
        self.detection_interval_spin.setRange(0.5, 10.0)
        self.detection_interval_spin.setValue(1.0)
        self.detection_interval_spin.setSingleStep(0.5)
        other_layout.addWidget(self.detection_interval_spin)
        
        self.safe_mode_check = QCheckBox("안전 모드")
        self.safe_mode_check.setChecked(True)
        other_layout.addWidget(self.safe_mode_check)
        layout.addLayout(other_layout)
        
        group.setLayout(layout)
        return group
        
    def create_control_group(self) -> QGroupBox:
        """컨트롤 그룹 생성"""
        group = QGroupBox("컨트롤")
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("시작")
        self.start_btn.clicked.connect(self.start_automation)
        layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("일시정지")
        self.pause_btn.clicked.connect(self.pause_automation)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("정지")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        group.setLayout(layout)
        return group
        
    def create_status_group(self) -> QGroupBox:
        """상태 표시 그룹 생성"""
        group = QGroupBox("상태")
        layout = QVBoxLayout()
        
        # 현재 상태
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("현재 상태:"))
        self.status_label = QLabel("대기 중")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        # 감지 통계
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("감지된 항목:"))
        self.before_count = QLabel("다운로드 전: 0")
        stats_layout.addWidget(self.before_count)
        self.downloading_count = QLabel("다운로드 중: 0")
        stats_layout.addWidget(self.downloading_count)
        self.completed_count = QLabel("완료: 0")
        stats_layout.addWidget(self.completed_count)
        layout.addLayout(stats_layout)
        
        # 진행률
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        group.setLayout(layout)
        return group
        
    def create_log_group(self) -> QGroupBox:
        """로그 그룹 생성"""
        group = QGroupBox("로그")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
        
    def setup_connections(self):
        """시그널/슬롯 연결 설정"""
        pass
        
    def select_template(self, status: ImageStatus):
        """템플릿 이미지 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"{status.value} 템플릿 선택",
            "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                self.detector.load_template(status, file_path)
                self.template_paths[status] = file_path
                
                # UI 업데이트
                filename = Path(file_path).name
                if status == ImageStatus.BEFORE_DOWNLOAD:
                    self.before_label.setText(filename)
                elif status == ImageStatus.DOWNLOADING:
                    self.downloading_label.setText(filename)
                elif status == ImageStatus.COMPLETED:
                    self.completed_label.setText(filename)
                    
                self.log(f"{status.value} 템플릿 로드: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "오류", f"템플릿 로드 실패: {str(e)}")
                
    def select_region(self):
        """영역 선택"""
        self.hide()  # 메인 윈도우 숨기기
        
        selector = RegionSelector()
        region = selector.select_region_interactive()
        
        self.show()  # 메인 윈도우 다시 표시
        
        if region:
            self.selected_region = region
            x, y, w, h = region
            self.region_label.setText(f"영역: ({x}, {y}) - 크기: {w}x{h}")
            self.log(f"영역 선택됨: {region}")
        else:
            self.log("영역 선택 취소됨")
            
    def start_automation(self):
        """자동화 시작"""
        # 검증
        if not all(self.template_paths.values()):
            QMessageBox.warning(self, "경고", "모든 템플릿 이미지를 선택해주세요.")
            return
            
        if not self.selected_region:
            QMessageBox.warning(self, "경고", "감지 영역을 선택해주세요.")
            return
            
        # 설정 생성
        config = AutomationConfig(
            scroll_speed=self.scroll_speed_spin.value(),
            scroll_pause=self.scroll_pause_spin.value(),
            click_pause=0.3,
            detection_interval=self.detection_interval_spin.value(),
            completion_threshold_high=self.high_threshold_spin.value() / 100.0,
            completion_threshold_low=self.low_threshold_spin.value() / 100.0,
            safe_mode=self.safe_mode_check.isChecked()
        )
        
        # 자동화 객체 생성
        self.automation = DownloadAutomation(self.detector, config)
        self.automation.set_region(self.selected_region)
        
        # 콜백 설정
        self.automation.on_state_change = self.on_state_change
        self.automation.on_detection = self.on_detection_update
        self.automation.on_click = lambda pos: self.log(f"클릭: {pos}")
        self.automation.on_scroll = lambda amount: self.log(f"스크롤: {amount}")
        self.automation.on_completion = lambda: self.log("자동화 완료!")
        
        # 시작
        if self.automation.start():
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.log("자동화 시작됨")
            
    def pause_automation(self):
        """자동화 일시정지"""
        if self.automation:
            if self.automation.state == AutomationState.RUNNING:
                self.automation.pause()
                self.pause_btn.setText("재개")
            elif self.automation.state == AutomationState.PAUSED:
                self.automation.resume()
                self.pause_btn.setText("일시정지")
                
    def stop_automation(self):
        """자동화 정지"""
        if self.automation:
            self.automation.stop()
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.pause_btn.setText("일시정지")
            self.log("자동화 정지됨")
            
    def on_state_change(self, state: AutomationState):
        """상태 변경 콜백"""
        self.status_label.setText(state.value)
        
    def on_detection_update(self, detections: Dict):
        """감지 업데이트 콜백"""
        before = len(detections.get(ImageStatus.BEFORE_DOWNLOAD, []))
        downloading = len(detections.get(ImageStatus.DOWNLOADING, []))
        completed = len(detections.get(ImageStatus.COMPLETED, []))
        
        self.before_count.setText(f"다운로드 전: {before}")
        self.downloading_count.setText(f"다운로드 중: {downloading}")
        self.completed_count.setText(f"완료: {completed}")
        
        # 진행률 계산
        total = before + downloading + completed
        if total > 0:
            progress = int((completed / total) * 100)
            self.progress_bar.setValue(progress)
            
    def log(self, message: str):
        """로그 메시지 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        """종료 이벤트"""
        if self.automation and self.automation.state == AutomationState.RUNNING:
            reply = QMessageBox.question(
                self, "확인",
                "자동화가 실행 중입니다. 종료하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.automation.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()