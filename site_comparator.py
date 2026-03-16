from ultralytics import YOLO
import cv2
from typing import Dict, List
from utils import setup_logging
from reference_scale_detector import ReferenceScaleDetector
from measurement_extractor import MeasurementExtractor
from element_matcher import ElementMatcher

class SiteComparator:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.model = YOLO(config['yolo_model'])
        self.scale_detector = ReferenceScaleDetector(self.model, logger)  # Phase 1: Reference scale detection
        self.measurement_extractor = MeasurementExtractor(logger)  # Phase 2: Better measurement extraction
        self.element_matcher = ElementMatcher(logger)  # Phase 3: Smart element matching

    def compare_site_photo(self, photo_path, pdf_length=10.0):
        try:
            img = cv2.imread(photo_path)
            
            # Phase 1: Detect reference scale automatically
            self.logger.info("🔍 Phase 1: Detecting reference scale...")
            scale_result = self.scale_detector.detect_scale_in_photo(photo_path)
            
            if not scale_result:
                self.logger.warning("⚠️ No reference scale detected - falling back to manual scale")
                scale = 100.0  # Fallback scale
                scale_info = "Manual fallback scale"
            else:
                scale = scale_result['scale']
                scale_info = self.scale_detector.get_scale_info_string(scale_result)
                self.logger.info(f"✅ Reference scale detected: {scale:.1f} pixels/meter")
            
            # Run YOLO detection
            self.logger.info("🔍 Running YOLO object detection...")
            results = self.model(img)
            boxes = results[0].boxes.xywh.cpu().numpy() if results[0].boxes else []
            
            if boxes.size > 0:
                real_width = boxes[0][2]  # First box width (pixels)
                site_length = real_width / scale  # Convert pixels to meters using detected scale
                diff = abs(pdf_length - site_length)
                diff_percent = (diff / pdf_length) * 100
                
                self.logger.info(f"📏 Measurement Comparison:")
                self.logger.info(f"   PDF: {pdf_length:.2f}m")
                self.logger.info(f"   Site: {site_length:.2f}m")
                self.logger.info(f"   Difference: {diff:.2f}m ({diff_percent:.1f}%)")
                self.logger.info(f"   {scale_info}")
                
                if diff_percent <= 5:
                    self.logger.info("✅ MATCH - Within tolerance")
                    return {"status": "Match", "confidence": (100 - diff_percent) / 100, "scale": scale}
                elif diff_percent <= 15:
                    self.logger.warning("⚠️ SMALL ISSUE - Minor difference detected")
                    return {"status": "Small Issue", "confidence": (100 - diff_percent) / 100, "scale": scale}
                else:
                    self.logger.error("🚨 BIG PROBLEM - Significant mismatch!")
                    return {"status": "Mismatch", "confidence": (100 - diff_percent) / 100, "scale": scale}
            else:
                self.logger.warning("⚠️ No objects detected in photo")
                return {"status": "No detection", "confidence": 0.0, "scale": scale}
        except Exception as e:
            self.logger.error(f"❌ Site comparison failed: {e}")
            return {"status": "Error", "confidence": 0.0, "scale": None}
    
    def analyze_photo(self, photo_path):
        """
        Comprehensive photo analysis including scale detection
        
        Returns detailed measurements and detections
        """
        try:
            img = cv2.imread(photo_path)
            if img is None:
                self.logger.error(f"❌ Could not load photo: {photo_path}")
                return None
            
            # Phase 1: Detect scale
            self.logger.info(f"📸 Analyzing photo: {photo_path}")
            scale_result = self.scale_detector.detect_scale_in_photo(photo_path)
            
            if not scale_result:
                self.logger.warning("⚠️ No reference scale found - analysis may be inaccurate")
                scale = 100.0
            else:
                scale = scale_result['scale']
                self.logger.info(f"✅ {self.scale_detector.get_scale_info_string(scale_result)}")
            
            # Run YOLO detection
            results = self.model(photo_path)
            boxes = results[0].boxes if results[0].boxes else None
            
            detections = []
            if boxes:
                for box in boxes:
                    x, y, w, h = box.xywh.cpu().numpy()[0]
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Convert to meters
                    width_m = w / scale
                    height_m = h / scale
                    
                    detection = {
                        'class': self.model.names[cls],
                        'confidence': conf,
                        'width_px': float(w),
                        'height_px': float(h),
                        'width_m': width_m,
                        'height_m': height_m,
                        'scale_used': scale
                    }
                    detections.append(detection)
                    
                    self.logger.info(f"   ✅ {detection['class']}: {width_m:.2f}m × {height_m:.2f}m (conf: {conf:.2f})")
            
            return {
                'photo': photo_path,
                'scale': scale,
                'scale_result': scale_result,
                'detections': detections
            }
            
        except Exception as e:
            self.logger.error(f"❌ Photo analysis failed: {e}")
            return None
    
    def extract_measurements_from_photo(self, photo_path):
        """
        Phase 2: Extract measurements from photo using advanced OCR
        
        Returns list of extracted measurements with units and values
        """
        try:
            self.logger.info(f"📊 Phase 2: Extracting measurements from photo...")
            
            # Get scale for reference
            scale_result = self.scale_detector.detect_scale_in_photo(photo_path)
            scale = scale_result['scale'] if scale_result else 100.0
            
            # Extract measurements using OCR
            measurements = self.measurement_extractor.extract_from_image(photo_path)
            
            if not measurements:
                self.logger.warning("⚠️ No measurements extracted from photo")
                return []
            
            # Validate measurements
            valid_measurements, invalid = self.measurement_extractor.validate_measurements(measurements)
            
            if invalid:
                self.logger.warning(f"⚠️ {len(invalid)} invalid measurements filtered out")
            
            self.logger.info(f"✅ Extracted {len(valid_measurements)} valid measurements")
            
            # Log summary
            summary = self.measurement_extractor.create_summary(valid_measurements)
            self.logger.info(f"📈 Measurement Summary: {summary['total']} total, {len(summary['by_type'])} types")
            
            return valid_measurements
            
        except Exception as e:
            self.logger.error(f"❌ Measurement extraction failed: {e}")
            return []
    
    def compare_measurements(self, site_measurements, pdf_measurements):
        """
        Phase 2+: Compare measurements from site vs PDF
        
        Returns comparison results with differences and categorization
        """
        try:
            self.logger.info(f"📊 Comparing {len(site_measurements)} site measurements with {len(pdf_measurements)} PDF measurements...")
            
            comparisons = []
            for site_m in site_measurements:
                # Find matching measurement type
                matching_pdf = [p for p in pdf_measurements if p['type'] == site_m['type']]
                
                if not matching_pdf:
                    self.logger.warning(f"⚠️ No PDF measurement found for type: {site_m['type']}")
                    continue
                
                for pdf_m in matching_pdf:
                    comparison = self.measurement_extractor.compare_measurements(
                        site_m['value_meters'],
                        pdf_m['value_meters']
                    )
                    comparison['site_measurement'] = site_m
                    comparison['pdf_measurement'] = pdf_m
                    comparisons.append(comparison)
                    
                    self.logger.info(f"   {comparison['label']} {site_m['type']}: {site_m['value_meters']:.4f}m vs {pdf_m['value_meters']:.4f}m")
            
            self.logger.info(f"✅ Completed comparison of {len(comparisons)} measurement pairs")
            return comparisons
            
        except Exception as e:
            self.logger.error(f"❌ Measurement comparison failed: {e}")
            return []
    
    def match_and_analyze(self, site_photo, pdf_photo):
        """
        Phase 3: Complete matching and analysis workflow
        
        1. Extract measurements from site photo
        2. Extract measurements from PDF photo
        3. Match measurements intelligently
        4. Detect anomalies
        5. Generate report
        
        Args:
            site_photo: Path to site photo
            pdf_photo: Path to PDF blueprint image
            
        Returns:
            Comprehensive matching report
        """
        try:
            self.logger.info(f"\n🔄 Phase 3: Starting complete match and analysis workflow...")
            
            # Extract from site
            self.logger.info(f"\n📸 Extracting from site photo: {site_photo}")
            site_measurements = self.extract_measurements_from_photo(site_photo)
            self.logger.info(f"✅ Site: {len(site_measurements)} measurements extracted")
            
            # Extract from PDF
            self.logger.info(f"\n📄 Extracting from PDF: {pdf_photo}")
            pdf_measurements = self.extract_measurements_from_photo(pdf_photo)
            self.logger.info(f"✅ PDF: {len(pdf_measurements)} measurements extracted")
            
            # Match measurements
            self.logger.info(f"\n🔗 Matching measurements...")
            matches = self.element_matcher.match_measurements(site_measurements, pdf_measurements)
            self.logger.info(f"✅ Matched: {len(matches)} measurement pairs")
            
            # Detect anomalies
            anomalies = self.element_matcher.detect_anomalies()
            
            # Get relationships
            relationships = self.element_matcher.get_element_relationships()
            
            # Generate full report
            report = self.element_matcher.generate_match_report()
            # Phase 4: Generate PDF/CSV report
            try:
                from report_generator import create_and_save_reports
                out_dir = self.config.get('report_output_dir', 'reports')
                create_and_save_reports(report, out_dir, self.logger)
            except Exception as e:
                self.logger.warning(f"⚠️ Report generation skipped: {e}")
            
            # Summary logging
            self.logger.info(f"\n📊 ANALYSIS SUMMARY")
            self.logger.info(f"   ✅ Matches: {len(matches)}")
            self.logger.info(f"   🚨 Missing in site: {len(anomalies['missing_in_site'])}")
            self.logger.info(f"   ⚠️  Extra in site: {len(anomalies['extra_in_site'])}")
            self.logger.info(f"   🔗 Relationships: {len(relationships['sequences'])}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Phase 3 analysis failed: {e}")
            return None
    
    def generate_comparison_summary(self) -> Dict:
        """
        Generate summary of latest matching operation
        
        Returns statistics and categorization
        """
        try:
            stats = self.element_matcher.get_statistics()
            self.logger.info(f"📈 Matching Statistics:")
            self.logger.info(f"   Average difference: {stats['average_difference']:.2f}%")
            self.logger.info(f"   Median difference: {stats['median_difference']:.2f}%")
            self.logger.info(f"   Success rate: {stats['match_success_rate']*100:.1f}%")
            return stats
        except Exception as e:
            self.logger.error(f"❌ Failed to generate summary: {e}")
            return None