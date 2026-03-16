"""
Reference Scale Detector Module
Purpose: Auto-detect reference objects (tape measure, brick) in construction photos
to calculate accurate scale (pixels per meter) for measurement conversion.

Author: Construction CV Inspector Team
Date: February 2026
Status: Phase 1 Implementation
"""

import cv2
import numpy as np
import logging
from typing import Optional, Dict, Tuple

class ReferenceScaleDetector:
    """
    Detects reference objects in photos (tape measure, brick) and calculates scale.
    
    Standard References:
    - Tape measure: Usually 1m, 3m, or 5m long
    - Standard brick: 19cm (190mm) length
    - Metal ruler: Usually labeled with measurements
    """
    
    def __init__(self, yolo_model, logger: logging.Logger = None):
        """
        Initialize Reference Scale Detector
        
        Args:
            yolo_model: Loaded YOLO model for object detection
            logger: Python logger instance
        """
        self.model = yolo_model
        self.logger = logger or logging.getLogger(__name__)
        
        # Standard reference sizes (in meters)
        self.TAPE_MEASURE_LENGTH = 1.0  # Common tape measure length
        self.BRICK_LENGTH = 0.19        # Standard brick = 19cm
        self.RULER_LENGTH = 0.3         # 30cm ruler
        
        # Scale validation bounds (pixels per meter)
        self.MIN_SCALE = 50      # At least 50 pixels per meter
        self.MAX_SCALE = 2000    # At most 2000 pixels per meter
        
        self.logger.info("✅ Reference Scale Detector initialized")
    
    def detect_scale_in_photo(self, image_path: str) -> Optional[Dict]:
        """
        Main function: Auto-detect reference scale in photo
        
        Args:
            image_path: Path to site photo
            
        Returns:
            Dict with scale info, or None if detection failed
            {
                'scale': 500.0,           # pixels per meter
                'reference_type': 'tape_measure',  # what was detected
                'reference_pixels': 500.0,
                'reference_meters': 1.0,
                'confidence': 0.92,
                'status': 'success'
            }
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                self.logger.error(f"❌ Could not load image: {image_path}")
                return None
            
            self.logger.info(f"🔍 Detecting reference scale in: {image_path}")
            
            # Try tape measure first (most reliable)
            result = self.detect_tape_measure(img)
            if result:
                self.logger.info(f"✅ Tape measure detected: {result}")
                return result
            
            # Try brick reference
            result = self.detect_brick_reference(img)
            if result:
                self.logger.info(f"✅ Brick reference detected: {result}")
                return result
            
            # Try ruler
            result = self.detect_ruler(img)
            if result:
                self.logger.info(f"✅ Ruler detected: {result}")
                return result
            
            self.logger.warning("⚠️ No reference scale detected in photo")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Scale detection failed: {e}")
            return None
    
    def detect_tape_measure(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect tape measure in image and extract length
        
        Uses YOLO to find 'tape_measure' class and measures its bounding box
        
        Args:
            image: OpenCV image
            
        Returns:
            Scale info dict or None
        """
        try:
            # Run YOLO inference
            results = self.model(image, conf=0.5)
            
            if not results or len(results) == 0:
                return None
            
            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                return None
            
            # Look for tape measure in detections
            for box in boxes:
                class_name = self.model.names[int(box.cls[0])]
                
                # Check if this is a tape measure
                if 'tape' in class_name.lower() or 'measure' in class_name.lower():
                    confidence = float(box.conf[0])
                    
                    # Get bounding box dimensions
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    width_px = x2 - x1
                    height_px = y2 - y1
                    
                    # Tape measure is usually longer than it is tall
                    tape_length_px = max(width_px, height_px)
                    
                    if tape_length_px < 50:  # Too small
                        continue
                    
                    # Calculate scale (assume tape measure is ~1m)
                    scale = tape_length_px / self.TAPE_MEASURE_LENGTH
                    
                    # Validate scale
                    if not self._validate_scale(scale):
                        continue
                    
                    return {
                        'scale': scale,
                        'reference_type': 'tape_measure',
                        'reference_pixels': tape_length_px,
                        'reference_meters': self.TAPE_MEASURE_LENGTH,
                        'confidence': confidence,
                        'status': 'success'
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Tape measure detection failed: {e}")
            return None
    
    def detect_brick_reference(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect brick in image and use as reference (19cm standard)
        
        Args:
            image: OpenCV image
            
        Returns:
            Scale info dict or None
        """
        try:
            results = self.model(image, conf=0.5)
            
            if not results or len(results) == 0:
                return None
            
            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                return None
            
            # Look for brick in detections
            for box in boxes:
                class_name = self.model.names[int(box.cls[0])]
                
                if 'brick' in class_name.lower():
                    confidence = float(box.conf[0])
                    
                    # Get bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    width_px = x2 - x1
                    height_px = y2 - y1
                    
                    # Standard brick: length is longest dimension
                    brick_length_px = max(width_px, height_px)
                    
                    if brick_length_px < 30:  # Too small
                        continue
                    
                    # Calculate scale (standard brick = 19cm)
                    scale = brick_length_px / self.BRICK_LENGTH
                    
                    if not self._validate_scale(scale):
                        continue
                    
                    return {
                        'scale': scale,
                        'reference_type': 'brick',
                        'reference_pixels': brick_length_px,
                        'reference_meters': self.BRICK_LENGTH,
                        'confidence': confidence,
                        'status': 'success'
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Brick detection failed: {e}")
            return None
    
    def detect_ruler(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect ruler or measuring stick
        
        Args:
            image: OpenCV image
            
        Returns:
            Scale info dict or None
        """
        try:
            results = self.model(image, conf=0.5)
            
            if not results or len(results) == 0:
                return None
            
            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                return None
            
            for box in boxes:
                class_name = self.model.names[int(box.cls[0])]
                
                if 'ruler' in class_name.lower() or 'scale' in class_name.lower():
                    confidence = float(box.conf[0])
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    ruler_length_px = max(x2 - x1, y2 - y1)
                    
                    if ruler_length_px < 30:
                        continue
                    
                    scale = ruler_length_px / self.RULER_LENGTH
                    
                    if not self._validate_scale(scale):
                        continue
                    
                    return {
                        'scale': scale,
                        'reference_type': 'ruler',
                        'reference_pixels': ruler_length_px,
                        'reference_meters': self.RULER_LENGTH,
                        'confidence': confidence,
                        'status': 'success'
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Ruler detection failed: {e}")
            return None
    
    def _validate_scale(self, scale: float) -> bool:
        """
        Validate that detected scale is reasonable
        
        Args:
            scale: Pixels per meter
            
        Returns:
            True if scale is valid, False otherwise
        """
        if scale < self.MIN_SCALE:
            self.logger.warning(f"⚠️ Scale too small ({scale:.1f} px/m) - Photo too far away?")
            return False
        
        if scale > self.MAX_SCALE:
            self.logger.warning(f"⚠️ Scale too large ({scale:.1f} px/m) - Photo too close?")
            return False
        
        return True
    
    def pixels_to_meters(self, pixels: float, scale: float) -> float:
        """
        Convert pixels to meters using scale
        
        Args:
            pixels: Number of pixels
            scale: Pixels per meter (from detect_scale_in_photo)
            
        Returns:
            Measurement in meters
        """
        if scale is None or scale == 0:
            self.logger.error("❌ Invalid scale for conversion")
            return None
        
        return pixels / scale
    
    def meters_to_pixels(self, meters: float, scale: float) -> float:
        """
        Convert meters to pixels using scale
        
        Args:
            meters: Measurement in meters
            scale: Pixels per meter
            
        Returns:
            Measurement in pixels
        """
        if scale is None or scale == 0:
            self.logger.error("❌ Invalid scale for conversion")
            return None
        
        return meters * scale
    
    def get_scale_info_string(self, scale_result: Dict) -> str:
        """
        Format scale result for display
        
        Args:
            scale_result: Result from detect_scale_in_photo()
            
        Returns:
            Formatted string
        """
        if not scale_result or scale_result['status'] != 'success':
            return "❌ No reference scale detected"
        
        ref_type = scale_result['reference_type']
        scale = scale_result['scale']
        ref_px = scale_result['reference_pixels']
        ref_m = scale_result['reference_meters']
        conf = scale_result['confidence']
        
        return (
            f"✅ Scale Detected\n"
            f"   Type: {ref_type}\n"
            f"   Reference: {ref_m*100:.0f}cm = {ref_px:.0f}px\n"
            f"   Scale: {scale:.1f} pixels/meter\n"
            f"   Confidence: {conf*100:.1f}%"
        )


# Standalone functions for easy use
def detect_scale(image_path: str, yolo_model, logger: logging.Logger = None) -> Optional[Dict]:
    """
    Convenience function to detect scale from image path
    
    Args:
        image_path: Path to site photo
        yolo_model: Loaded YOLO model
        logger: Optional logger
        
    Returns:
        Scale info dict or None
    """
    detector = ReferenceScaleDetector(yolo_model, logger)
    return detector.detect_scale_in_photo(image_path)
