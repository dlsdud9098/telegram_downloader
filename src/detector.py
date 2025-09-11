# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import mss
import platform
import os

class ImageDetector:
    def __init__(self):
        self.templates = {}
        
    def load_templates(self, template_paths: dict):
        print(f"Loading templates from: {template_paths}")
        for name, path in template_paths.items():
            # Convert path for Windows compatibility
            if platform.system() == 'Windows':
                path = path.replace('/', '\\')
            
            print(f"Attempting to load {name} from {path}")
            if os.path.exists(path):
                print(f"  File exists: {path}")
                img = cv2.imread(path)
                if img is not None:
                    h, w = img.shape[:2]
                    print(f"  Loaded successfully: {w}x{h} pixels")
                    self.templates[name] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    print(f"  ERROR: cv2.imread failed for {path}")
            else:
                print(f"  ERROR: File not found: {path}")
                print(f"  Current directory: {os.getcwd()}")
                print(f"  Directory contents: {os.listdir('.')}")
    
    def capture_region(self, region: dict) -> np.ndarray:
        # Always create a new mss instance for each capture to avoid thread issues
        try:
            with mss.mss() as sct:
                screenshot = sct.grab(region)
                img = np.array(screenshot)
                # Windows might need different color conversion
                if platform.system() == 'Windows':
                    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                else:
                    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            print(f"Error capturing region: {e}")
            raise
    
    def detect_images(self, region: dict, threshold: float = 0.5) -> dict:
        screen = self.capture_region(region)
        gray_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        screen_h, screen_w = gray_screen.shape
        
        # Platform-specific threshold adjustment
        if platform.system() == 'Windows':
            # Windows needs lower threshold due to rendering differences
            threshold = threshold * 0.5  # Use 25% instead of 50%
            print(f"Windows detected: Using lower threshold {threshold:.2f}")
        
        # Debug output for first detection
        if not hasattr(self, '_first_detection_done'):
            print(f"Screen capture size: {screen_w}x{screen_h}")
            print(f"Number of templates loaded: {len(self.templates)}")
            print(f"Platform: {platform.system()}")
            print(f"Base threshold: {threshold:.2f}")
            # Save captured screen for debugging
            cv2.imwrite("debug_screen_capture.jpg", screen)
            cv2.imwrite("debug_screen_gray.jpg", gray_screen)
            print("Saved debug images: debug_screen_capture.jpg and debug_screen_gray.jpg")
            self._first_detection_done = True
        
        results = {}
        for name, template in self.templates.items():
            h, w = template.shape
            
            # Skip if template is larger than the screen region
            if h > screen_h or w > screen_w:
                if not hasattr(self, f'_warned_{name}'):
                    print(f"Warning: Template '{name}' ({w}x{h}) is larger than selected region ({screen_w}x{screen_h}). Skipping.")
                    setattr(self, f'_warned_{name}', True)
                results[name] = []
                continue
            
            # Use only TM_CCOEFF_NORMED for better accuracy
            # Other methods give too many false positives
            best_method = 'TM_CCOEFF_NORMED'
            best_method_type = cv2.TM_CCOEFF_NORMED
            
            res = cv2.matchTemplate(gray_screen, template, best_method_type)
            best_score = np.max(res)
            best_res = res
            
            # Use the best method result
            res = best_res
            
            if res is None:
                print(f"  WARNING: No result for {name}")
                results[name] = []
                continue
            
            # Debug output - show all scores above 0.1 for debugging
            if best_score > 0.1:
                print(f"  {name}: best_score = {best_score:.3f} using {best_method}")
                
                # Save template comparison for first detection
                if not hasattr(self, f'_saved_{name}'):
                    cv2.imwrite(f"debug_template_{name}.jpg", template)
                    setattr(self, f'_saved_{name}', True)
            
            # Use appropriate threshold for TM_CCOEFF_NORMED
            # This method works best for icon detection
            actual_threshold = 0.5  # Moderate threshold for CCOEFF
            
            if not hasattr(self, f'_thresh_debug_{name}'):
                print(f"    Using threshold: {actual_threshold:.3f} for method {best_method}")
                setattr(self, f'_thresh_debug_{name}', True)
            
            # For SQDIFF_NORMED, we need to find minimums
            if best_method_type == cv2.TM_SQDIFF_NORMED:
                # For SQDIFF, find values below threshold (lower is better in original res)
                loc = np.where(res <= actual_threshold)
                if not hasattr(self, f'_debug_{name}'):
                    print(f"    SQDIFF: Looking for values <= {actual_threshold:.3f}")
                    print(f"    Min value in res: {np.min(res):.3f}, Max: {np.max(res):.3f}")
                    setattr(self, f'_debug_{name}', True)
            else:
                # For other methods, find values above threshold (higher is better)
                loc = np.where(res >= actual_threshold)
                if not hasattr(self, f'_debug_{name}'):
                    print(f"    Looking for values >= {actual_threshold:.3f}")
                    print(f"    Max value in res: {np.max(res):.3f}, Min: {np.min(res):.3f}")
                    print(f"    Number of pixels above threshold: {np.sum(res >= actual_threshold)}")
                    setattr(self, f'_debug_{name}', True)
            
            matches = []
            raw_points = list(zip(*loc[::-1]))
            
            # Debug: show raw match count
            if raw_points and not hasattr(self, f'_raw_debug_{name}'):
                print(f"    Raw matches found: {len(raw_points)}")
                if len(raw_points) > 30:
                    print(f"    Reducing to top matches...")
                    # Get scores for each point and sort by score
                    point_scores = []
                    for pt in raw_points[:500]:  # Limit to first 500 to avoid memory issues
                        if pt[1] < res.shape[0] and pt[0] < res.shape[1]:
                            point_scores.append((pt, res[pt[1], pt[0]]))
                    
                    # Sort by score (higher is better for CCOEFF)
                    point_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Take only top 10 matches for more accuracy
                    raw_points = [ps[0] for ps in point_scores[:10]]
                    print(f"    Reduced to top 10 matches by score")
                setattr(self, f'_raw_debug_{name}', True)
            
            for pt in raw_points:
                center_x = pt[0] + w // 2 + region['left']
                center_y = pt[1] + h // 2 + region['top']
                matches.append((center_x, center_y))
            
            if matches:
                before_dedup = len(matches)
                matches = self._remove_duplicates(matches)
                if matches:  # After removing duplicates
                    print(f"    Found {len(matches)} {name} image(s) (was {before_dedup} before deduplication)")
            
            results[name] = matches
            
        return results
    
    def _remove_duplicates(self, matches: List[Tuple[int, int]], threshold: int = 30) -> List[Tuple[int, int]]:
        if not matches:
            return []
        
        unique_matches = []
        for match in matches:
            is_duplicate = False
            for unique in unique_matches:
                if abs(match[0] - unique[0]) < threshold and abs(match[1] - unique[1]) < threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_matches.append(match)
        
        return unique_matches
    
    def get_detection_stats(self, results: dict) -> dict:
        # Count each type of image
        not_downloaded_count = len(results.get('not_downloaded', []))
        downloading_count = len(results.get('downloading', []))
        downloaded_count = len(results.get('downloaded', []))
        
        # Total is sum of all detected images
        total = not_downloaded_count + downloading_count + downloaded_count
        
        stats = {
            'total': total,
            'not_downloaded': not_downloaded_count,
            'downloading': downloading_count,
            'downloaded': downloaded_count,
        }
        
        # Calculate percentage based on downloaded (completed) images only
        if total > 0:
            stats['downloaded_percentage'] = (downloaded_count / total) * 100
            # Debug output
            print(f"Stats - Total: {total}, Downloaded: {downloaded_count}, Downloading: {downloading_count}, Not Downloaded: {not_downloaded_count}")
            print(f"Downloaded percentage: {stats['downloaded_percentage']:.1f}%")
        else:
            stats['downloaded_percentage'] = 0
            
        return stats