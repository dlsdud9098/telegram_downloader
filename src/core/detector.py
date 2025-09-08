import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class DownloadState(Enum):
    NOT_DOWNLOADED = "not_download"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"


@dataclass
class Detection:
    state: DownloadState
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    center: Tuple[int, int]


class ImageDetector:
    def __init__(self, template_dir: str = "images"):
        self.template_dir = Path(template_dir)
        self.templates = self._load_templates()
        self.detection_threshold = 0.9  # 90% match as per requirements
        
    def _load_templates(self) -> Dict[DownloadState, np.ndarray]:
        templates = {}
        template_files = {
            DownloadState.NOT_DOWNLOADED: "not_download.jpg",
            DownloadState.DOWNLOADING: "downloading.jpg",
            DownloadState.DOWNLOADED: "downloaded.jpg"
        }
        
        for state, filename in template_files.items():
            filepath = self.template_dir / filename
            if filepath.exists():
                template = cv2.imread(str(filepath))
                if template is not None:
                    templates[state] = template
                else:
                    print(f"Warning: Could not load template {filepath}")
            else:
                print(f"Warning: Template file not found: {filepath}")
                
        return templates
    
    def detect_images(self, screenshot: np.ndarray) -> List[Detection]:
        detections = []
        
        for state, template in self.templates.items():
            matches = self._find_matches(screenshot, template, state)
            detections.extend(matches)
            
        # Remove overlapping detections
        detections = self._remove_overlaps(detections)
        return detections
    
    def _find_matches(self, screenshot: np.ndarray, template: np.ndarray, 
                     state: DownloadState) -> List[Detection]:
        if template is None or screenshot is None:
            return []
            
        # Convert to grayscale for template matching
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        h, w = gray_template.shape
        detections = []
        
        # Method 1: Template Matching
        result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= self.detection_threshold)
        
        for pt in zip(*locations[::-1]):
            bbox = (pt[0], pt[1], w, h)
            center = (pt[0] + w // 2, pt[1] + h // 2)
            confidence = result[pt[1], pt[0]]
            
            detections.append(Detection(
                state=state,
                bbox=bbox,
                confidence=float(confidence),
                center=center
            ))
        
        # Method 2: Feature Matching (SIFT/ORB) for scale invariance
        detections.extend(self._feature_matching(screenshot, template, state))
        
        return detections
    
    def _feature_matching(self, screenshot: np.ndarray, template: np.ndarray,
                         state: DownloadState) -> List[Detection]:
        detections = []
        
        try:
            # Use ORB detector (free and fast)
            orb = cv2.ORB_create()
            
            # Find keypoints and descriptors
            kp1, des1 = orb.detectAndCompute(template, None)
            kp2, des2 = orb.detectAndCompute(screenshot, None)
            
            if des1 is None or des2 is None:
                return detections
            
            # Match features
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # If we have enough good matches, consider it a detection
            if len(matches) > 10:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                
                # Find homography
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if M is not None:
                    h, w = template.shape[:2]
                    pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                    dst = cv2.perspectiveTransform(pts, M)
                    
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(dst)
                    if w > 10 and h > 10:  # Minimum size check
                        center = (x + w // 2, y + h // 2)
                        confidence = min(1.0, len(matches) / 20.0)  # Normalize confidence
                        
                        if confidence >= self.detection_threshold:
                            detections.append(Detection(
                                state=state,
                                bbox=(x, y, w, h),
                                confidence=confidence,
                                center=center
                            ))
        except Exception as e:
            print(f"Feature matching error: {e}")
            
        return detections
    
    def _remove_overlaps(self, detections: List[Detection]) -> List[Detection]:
        if not detections:
            return []
        
        # Sort by confidence
        detections.sort(key=lambda x: x.confidence, reverse=True)
        
        final_detections = []
        for detection in detections:
            overlapping = False
            for final_det in final_detections:
                if self._iou(detection.bbox, final_det.bbox) > 0.5:
                    overlapping = True
                    break
            if not overlapping:
                final_detections.append(detection)
                
        return final_detections
    
    def _iou(self, box1: Tuple[int, int, int, int], 
            box2: Tuple[int, int, int, int]) -> float:
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate intersection
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        if xi2 < xi1 or yi2 < yi1:
            return 0.0
        
        intersection = (xi2 - xi1) * (yi2 - yi1)
        union = w1 * h1 + w2 * h2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def set_threshold(self, threshold: float):
        self.detection_threshold = max(0.0, min(1.0, threshold))