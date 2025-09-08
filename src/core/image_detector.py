import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ImageStatus(Enum):
    """이미지 상태 열거형"""
    BEFORE_DOWNLOAD = "before_download"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"


@dataclass
class DetectionResult:
    """이미지 감지 결과를 담는 데이터 클래스"""
    status: ImageStatus
    position: Tuple[int, int]
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height


class ImageDetector:
    """템플릿 매칭을 사용한 이미지 감지 클래스"""
    
    def __init__(self, threshold: float = 0.8):
        """
        Args:
            threshold: 매칭 임계값 (0.0 ~ 1.0)
        """
        self.threshold = threshold
        self.templates: Dict[ImageStatus, np.ndarray] = {}
        self.template_sizes: Dict[ImageStatus, Tuple[int, int]] = {}
        
    def load_template(self, status: ImageStatus, template_path: str) -> None:
        """템플릿 이미지 로드
        
        Args:
            status: 이미지 상태
            template_path: 템플릿 이미지 경로
        """
        if not Path(template_path).exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
            
        template = cv2.imread(template_path)
        if template is None:
            raise ValueError(f"Failed to load template: {template_path}")
            
        self.templates[status] = template
        self.template_sizes[status] = (template.shape[1], template.shape[0])
        
    def detect_single(self, screen_image: np.ndarray, status: ImageStatus) -> List[DetectionResult]:
        """단일 템플릿에 대한 감지 수행
        
        Args:
            screen_image: 검색할 화면 이미지
            status: 찾을 이미지 상태
            
        Returns:
            감지된 결과 리스트
        """
        if status not in self.templates:
            raise ValueError(f"Template for {status} not loaded")
            
        template = self.templates[status]
        result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
        
        # 임계값 이상인 모든 매칭 찾기
        locations = np.where(result >= self.threshold)
        
        detections = []
        w, h = self.template_sizes[status]
        
        # 중복 제거를 위한 Non-Maximum Suppression
        points = list(zip(*locations[::-1]))
        points = self._non_max_suppression(points, w, h)
        
        for pt in points:
            confidence = result[pt[1], pt[0]]
            detection = DetectionResult(
                status=status,
                position=(pt[0] + w//2, pt[1] + h//2),  # 중심점
                confidence=float(confidence),
                bbox=(pt[0], pt[1], w, h)
            )
            detections.append(detection)
            
        return detections
    
    def detect_all(self, screen_image: np.ndarray) -> Dict[ImageStatus, List[DetectionResult]]:
        """모든 템플릿에 대한 감지 수행
        
        Args:
            screen_image: 검색할 화면 이미지
            
        Returns:
            상태별 감지 결과 딕셔너리
        """
        results = {}
        for status in self.templates.keys():
            results[status] = self.detect_single(screen_image, status)
        return results
    
    def _non_max_suppression(self, points: List[Tuple[int, int]], 
                            width: int, height: int, 
                            overlap_thresh: float = 0.3) -> List[Tuple[int, int]]:
        """겹치는 감지 결과 제거
        
        Args:
            points: 감지된 포인트들
            width: 템플릿 너비
            height: 템플릿 높이
            overlap_thresh: 겹침 임계값
            
        Returns:
            중복이 제거된 포인트 리스트
        """
        if not points:
            return []
            
        # 바운딩 박스로 변환
        boxes = []
        for (x, y) in points:
            boxes.append([x, y, x + width, y + height])
        boxes = np.array(boxes)
        
        # 면적 계산
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        
        # 정렬
        idxs = np.argsort(boxes[:, 3])
        
        pick = []
        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            
            # 겹침 계산
            xx1 = np.maximum(boxes[i, 0], boxes[idxs[:last], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[idxs[:last], 1])
            xx2 = np.minimum(boxes[i, 2], boxes[idxs[:last], 2])
            yy2 = np.minimum(boxes[i, 3], boxes[idxs[:last], 3])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            
            overlap = (w * h) / areas[idxs[:last]]
            
            idxs = np.delete(idxs, np.concatenate(([last],
                np.where(overlap > overlap_thresh)[0])))
        
        return [(boxes[i][0], boxes[i][1]) for i in pick]
    
    def calculate_completion_ratio(self, detections: Dict[ImageStatus, List[DetectionResult]]) -> float:
        """다운로드 완료 비율 계산
        
        Args:
            detections: 상태별 감지 결과
            
        Returns:
            완료된 항목의 비율 (0.0 ~ 1.0)
        """
        total_count = sum(len(det_list) for det_list in detections.values())
        if total_count == 0:
            return 0.0
            
        completed_count = len(detections.get(ImageStatus.COMPLETED, []))
        return completed_count / total_count