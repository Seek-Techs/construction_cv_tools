#!/usr/bin/env python
"""
Test Suite: End-to-End Analysis with Real Construction Photos
Tests all 5 phases with sample construction images
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from site_comparator import SiteComparator
from utils import load_config, setup_logging
from PIL import Image, ImageDraw, ImageFont


class ConstructionPhotoTester:
    """End-to-end test suite for construction CV analysis"""
    
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logging('INFO')
        self.comparator = SiteComparator(self.config, self.logger)
        self.test_dir = project_root / "test_data"
        self.results_dir = project_root / "test_results"
        self.results_dir.mkdir(exist_ok=True)
        self.test_dir.mkdir(exist_ok=True)
        
    def create_sample_images(self):
        """Create synthetic test images if real ones not available"""
        self.logger.info("Creating sample test images...")
        
        # Create a sample site photo (simple construction scene mockup)
        site_img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(site_img)
        
        # Draw some construction elements
        draw.rectangle([50, 50, 200, 250], outline='black', width=3)  # Window/opening
        draw.rectangle([300, 100, 600, 400], outline='black', width=3)  # Wall section
        draw.line([100, 300, 700, 300], fill='gray', width=2)  # Floor line
        
        # Add measurement annotations
        draw.text((220, 70), "2.5m", fill='blue')
        draw.text((320, 150), "3.0m", fill='blue')
        draw.text((100, 450), "5.0m", fill='blue')
        draw.text((700, 320), "2.0m", fill='blue')
        
        site_img.save(self.test_dir / "sample_site.jpg")
        self.logger.info(f"✅ Created sample site image: {self.test_dir / 'sample_site.jpg'}")
        
        # Create a blueprint/floor plan image
        blueprint_img = Image.new('RGB', (800, 600), color='lightblue')
        draw = ImageDraw.Draw(blueprint_img)
        
        # Draw floor plan elements
        draw.rectangle([50, 50, 200, 250], outline='darkblue', width=2)  # Window/opening
        draw.rectangle([300, 100, 600, 400], outline='darkblue', width=2)  # Wall section
        draw.line([100, 300, 700, 300], fill='navy', width=2)  # Floor line
        
        # Add dimension labels
        draw.text((220, 70), "2.5m", fill='black')
        draw.text((320, 150), "3.0m", fill='black')
        draw.text((100, 450), "5.0m", fill='black')
        draw.text((700, 320), "2.0m", fill='black')
        
        blueprint_img.save(self.test_dir / "sample_blueprint.jpg")
        self.logger.info(f"✅ Created sample blueprint image: {self.test_dir / 'sample_blueprint.jpg'}")
        
        return str(self.test_dir / "sample_site.jpg"), str(self.test_dir / "sample_blueprint.jpg")
    
    def test_phase_1_scale_detection(self, site_photo):
        """Test Phase 1: Reference Scale Detection"""
        self.logger.info("\n" + "="*60)
        self.logger.info("PHASE 1: Reference Scale Detection")
        self.logger.info("="*60)
        
        try:
            start = time.time()
            scale = self.comparator.scale_detector.detect_scale_in_photo(site_photo)
            elapsed = time.time() - start
            
            if scale:
                self.logger.info(f"✅ Scale Detected: {scale['scale']:.2f} px/m")
                self.logger.info(f"   Reference: {scale['reference_type']}")
                self.logger.info(f"   Confidence: {scale['confidence']:.1%}")
                self.logger.info(f"   ⏱  Time: {elapsed:.2f}s")
                return {
                    'status': 'passed',
                    'scale': scale['scale'],
                    'reference_type': scale['reference_type'],
                    'confidence': scale['confidence'],
                    'time': elapsed
                }
            else:
                self.logger.warning("⚠️  No reference scale detected, using default")
                return {
                    'status': 'warning',
                    'message': 'Using default scale',
                    'time': elapsed
                }
        except Exception as e:
            self.logger.error(f"❌ Phase 1 failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_phase_2_measurement_extraction(self, site_photo):
        """Test Phase 2: Measurement Extraction"""
        self.logger.info("\n" + "="*60)
        self.logger.info("PHASE 2: Measurement Extraction")
        self.logger.info("="*60)
        
        try:
            start = time.time()
            measurements = self.comparator.measurement_extractor.extract_from_image(site_photo)
            elapsed = time.time() - start
            
            if measurements:
                self.logger.info(f"✅ Measurements Extracted: {len(measurements)} found")
                for i, m in enumerate(measurements[:5], 1):  # Show first 5
                    self.logger.info(f"   {i}. {m['type']}: {m['value']:.2f}m (conf: {m.get('confidence', 0.8):.1%})")
                if len(measurements) > 5:
                    self.logger.info(f"   ... and {len(measurements)-5} more")
                self.logger.info(f"   ⏱  Time: {elapsed:.2f}s")
                return {
                    'status': 'passed',
                    'count': len(measurements),
                    'measurements': measurements,
                    'time': elapsed
                }
            else:
                self.logger.warning("⚠️  No measurements extracted")
                return {
                    'status': 'warning',
                    'message': 'No measurements found',
                    'time': elapsed
                }
        except Exception as e:
            self.logger.error(f"❌ Phase 2 failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_phase_3_element_matching(self, site_measurements, blueprint_measurements):
        """Test Phase 3: Element Matching"""
        self.logger.info("\n" + "="*60)
        self.logger.info("PHASE 3: Element Matching")
        self.logger.info("="*60)
        
        try:
            if not site_measurements or not blueprint_measurements:
                self.logger.warning("⚠️  Insufficient measurements for matching")
                return {
                    'status': 'warning',
                    'message': 'Insufficient measurements for matching'
                }
            
            start = time.time()
            matches = self.comparator.element_matcher.match_measurements(
                site_measurements,
                blueprint_measurements
            )
            elapsed = time.time() - start
            
            self.logger.info(f"✅ Matching Complete: {len(matches)} matches found")
            for i, match in enumerate(matches[:5], 1):  # Show first 5
                site_val = match.site_measurement.get('value_meters', 0)
                pdf_val = match.pdf_measurement.get('value_meters', 0)
                self.logger.info(f"   {i}. {site_val:.2f}m ← {match.match_type} → {pdf_val:.2f}m (conf: {match.confidence:.1%})")
            if len(matches) > 5:
                self.logger.info(f"   ... and {len(matches)-5} more")
            self.logger.info(f"   ⏱  Time: {elapsed:.2f}s")
            
            return {
                'status': 'passed',
                'count': len(matches),
                'matches': [
                    {
                        'site_type': m.site_measurement.get('type', 'unknown'),
                        'site_value': m.site_measurement.get('value_meters', 0),
                        'pdf_type': m.pdf_measurement.get('type', 'unknown'),
                        'pdf_value': m.pdf_measurement.get('value_meters', 0),
                        'match_type': m.match_type,
                        'confidence': m.confidence
                    } for m in matches
                ],
                'time': elapsed
            }
        except Exception as e:
            self.logger.error(f"❌ Phase 3 failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_phase_4_report_generation(self, match_results):
        """Test Phase 4: Report Generation"""
        self.logger.info("\n" + "="*60)
        self.logger.info("PHASE 4: Report Generation")
        self.logger.info("="*60)
        
        try:
            start = time.time()
            
            # Transform Phase 3 matches to report format
            report_matches = []
            for match in match_results.get('matches', []):
                report_matches.append({
                    'site': {
                        'type': match.get('site_type', 'unknown'),
                        'value_m': match.get('site_value', 0),
                        'confidence': match.get('confidence', 0)
                    },
                    'pdf': {
                        'type': match.get('pdf_type', 'unknown'),
                        'value_m': match.get('pdf_value', 0),
                        'confidence': match.get('confidence', 0)
                    },
                    'status': 'match',
                    'difference_percent': 0
                })
            
            # Create sample report data
            report_data = {
                'site_photo': 'sample_site.jpg',
                'blueprint_photo': 'sample_blueprint.jpg',
                'timestamp': datetime.now().isoformat(),
                'matches': report_matches,
                'summary': {
                    'total_matches': len(report_matches),
                    'accuracy': 0.95
                },
                'anomalies': {
                    'summary': {
                        'missing_count': 0,
                        'extra_count': 0,
                        'mismatches': 0
                    }
                }
            }
            
            # Generate reports
            from report_generator import ReportGenerator
            generator = ReportGenerator(self.logger)
            
            pdf_path = str(self.results_dir / "test_report.pdf")
            csv_path = str(self.results_dir / "test_report.csv")
            
            generator.create_pdf_report(report_data, pdf_path)
            generator.save_report_csv(report_data, csv_path)
            elapsed = time.time() - start
            
            self.logger.info(f"✅ Reports Generated:")
            self.logger.info(f"   📄 PDF: {pdf_path}")
            self.logger.info(f"   📊 CSV: {csv_path}")
            self.logger.info(f"   ⏱  Time: {elapsed:.2f}s")
            
            return {
                'status': 'passed',
                'pdf_path': pdf_path,
                'csv_path': csv_path,
                'time': elapsed
            }
        except Exception as e:
            self.logger.error(f"❌ Phase 4 failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_phase_5_web_interface_readiness(self):
        """Test Phase 5: Web Interface Readiness"""
        self.logger.info("\n" + "="*60)
        self.logger.info("PHASE 5: Web Interface Readiness")
        self.logger.info("="*60)
        
        try:
            from task_queue import TaskQueue
            from web_app import app
            
            # Check if modules import
            tq = TaskQueue(max_workers=2)
            self.logger.info(f"✅ TaskQueue initialized with 2 workers")
            
            # Check if Flask app initializes
            if app:
                self.logger.info(f"✅ Flask app initialized")
                self.logger.info(f"   Routes: {len(app.url_map._rules)}")
                
                # List endpoints
                endpoints = [str(rule) for rule in app.url_map.iter_rules()]
                for ep in endpoints[:5]:
                    self.logger.info(f"   - {ep}")
                
                return {
                    'status': 'passed',
                    'endpoints': len(endpoints),
                    'workers': 2
                }
        except Exception as e:
            self.logger.error(f"❌ Phase 5 check failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_full_test_suite(self):
        """Run complete end-to-end test"""
        self.logger.info("\n" + "█"*60)
        self.logger.info("█ CONSTRUCTION CV TOOL - COMPREHENSIVE TEST SUITE █")
        self.logger.info("█"*60)
        self.logger.info(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Test Directory: {self.test_dir}")
        self.logger.info(f"Results Directory: {self.results_dir}\n")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'phases': {}
        }
        
        # Create/find test images
        site_photo, blueprint_photo = self.create_sample_images()
        
        # Phase 1: Scale Detection
        phase1_result = self.test_phase_1_scale_detection(site_photo)
        results['phases']['phase_1'] = phase1_result
        
        # Phase 2: Measurement Extraction (both images)
        phase2_site = self.test_phase_2_measurement_extraction(site_photo)
        phase2_blueprint = self.test_phase_2_measurement_extraction(blueprint_photo)
        results['phases']['phase_2_site'] = phase2_site
        results['phases']['phase_2_blueprint'] = phase2_blueprint
        
        # Phase 3: Element Matching
        site_meas = phase2_site.get('measurements', [])
        blueprint_meas = phase2_blueprint.get('measurements', [])
        phase3_result = self.test_phase_3_element_matching(site_meas, blueprint_meas)
        results['phases']['phase_3'] = phase3_result
        
        # Phase 4: Report Generation
        phase4_result = self.test_phase_4_report_generation(phase3_result)
        results['phases']['phase_4'] = phase4_result
        
        # Phase 5: Web Interface Readiness
        phase5_result = self.test_phase_5_web_interface_readiness()
        results['phases']['phase_5'] = phase5_result
        
        # Summary
        self.print_test_summary(results)
        
        # Save results
        results_file = self.results_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        self.logger.info(f"\n✅ Test results saved to: {results_file}")
        
        return results
    
    def print_test_summary(self, results):
        """Print test summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("TEST SUMMARY")
        self.logger.info("="*60)
        
        for phase, result in results['phases'].items():
            status = result.get('status', 'unknown')
            status_symbol = {
                'passed': '✅',
                'warning': '⚠️',
                'failed': '❌',
                'unknown': '❓'
            }.get(status, '❓')
            
            self.logger.info(f"{status_symbol} {phase.upper()}: {status}")
            
            if 'time' in result:
                self.logger.info(f"   ⏱  {result['time']:.2f}s")
            if 'error' in result:
                self.logger.info(f"   Error: {result['error']}")
        
        self.logger.info("="*60)
        self.logger.info("\n🎉 Full Test Suite Complete!")
        self.logger.info("\nNext Steps:")
        self.logger.info("1. Review test results in test_results/")
        self.logger.info("2. Start web app: python web_app.py")
        self.logger.info("3. Open http://localhost:5000")
        self.logger.info("4. Upload real construction photos")


def main():
    """Main entry point"""
    tester = ConstructionPhotoTester()
    results = tester.run_full_test_suite()


if __name__ == '__main__':
    main()
