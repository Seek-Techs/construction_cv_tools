"""
Element Matcher Module (Phase 3)
Purpose: Match measurements from site photos to PDF blueprint elements
and determine correspondence/differences

Features:
- Spatial matching algorithms
- Type-based matching (same measurement types)
- Confidence scoring
- Anomaly detection
- Relationship tracking

Author: Construction CV Inspector Team
Date: February 2026
Status: Phase 3 Implementation
"""

import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class ElementMatch:
    """Represents a matched pair of measurements"""
    site_measurement: Dict
    pdf_measurement: Dict
    match_type: str  # 'exact', 'type', 'spatial', 'inferred'
    confidence: float  # 0.0 - 1.0
    difference_percent: float
    status: str  # 'match', 'issue', 'problem'
    notes: str = ""

class ElementMatcher:
    """
    Match measurements from site to PDF elements
    
    Handles:
    - Type-based matching (both meters, both diameters, etc.)
    - Spatial proximity matching
    - Confidence scoring
    - Anomaly detection
    - Relationship inference
    """
    
    def __init__(self, logger: logging.Logger = None):
        """Initialize Element Matcher"""
        self.logger = logger or logging.getLogger(__name__)
        self.matches: List[ElementMatch] = []
        self.unmatched_site: List[Dict] = []
        self.unmatched_pdf: List[Dict] = []
        
        # Tolerance thresholds
        self.MATCH_THRESHOLD = 0.05      # 5% = Match ✅
        self.ISSUE_THRESHOLD = 0.15      # 15% = Issue ⚠️
        # > 15% = Problem 🚨
        
        self.logger.info("✅ Element Matcher initialized")
    
    def match_measurements(self, site_measurements: List[Dict], 
                          pdf_measurements: List[Dict]) -> List[ElementMatch]:
        """
        Match site measurements to PDF elements
        
        Strategy:
        1. First pass: Exact type match (meter to meter, diameter to diameter)
        2. Second pass: Spatial proximity (if available)
        3. Third pass: Value-based inference
        
        Args:
            site_measurements: Measurements extracted from site photos
            pdf_measurements: Measurements extracted from PDF
            
        Returns:
            List of ElementMatch objects
        """
        self.logger.info(f"🔄 Matching {len(site_measurements)} site measurements to {len(pdf_measurements)} PDF elements...")
        
        self.matches = []
        self.unmatched_site = list(site_measurements)
        self.unmatched_pdf = list(pdf_measurements)
        
        # Pass 1: Exact type matching
        self._match_by_type()
        
        # Pass 2: Spatial proximity matching (if location data available)
        self._match_by_proximity()
        
        # Pass 3: Value-based inference
        self._match_by_value()
        
        self.logger.info(f"✅ Matching complete: {len(self.matches)} matches, "
                        f"{len(self.unmatched_site)} unmatched site, "
                        f"{len(self.unmatched_pdf)} unmatched PDF")
        
        return self.matches
    
    def _match_by_type(self):
        """Pass 1: Match measurements of same type"""
        self.logger.info("   📍 Pass 1: Matching by type...")
        
        matched_site = []
        matched_pdf = []
        
        for site_m in list(self.unmatched_site):
            # Find all PDF measurements of same type
            same_type_pdf = [p for p in self.unmatched_pdf if p['type'] == site_m['type']]
            
            if not same_type_pdf:
                continue
            
            # Find best match (closest value)
            best_pdf = min(same_type_pdf, 
                          key=lambda p: abs(p['value_meters'] - site_m['value_meters']))
            
            # Calculate difference
            diff_pct = abs(best_pdf['value_meters'] - site_m['value_meters']) / \
                      best_pdf['value_meters'] * 100 if best_pdf['value_meters'] != 0 else 0
            
            # Determine status
            if diff_pct <= self.MATCH_THRESHOLD * 100:
                status = 'match'
            elif diff_pct <= self.ISSUE_THRESHOLD * 100:
                status = 'issue'
            else:
                status = 'problem'
            
            # Create match
            match = ElementMatch(
                site_measurement=site_m,
                pdf_measurement=best_pdf,
                match_type='exact_type',
                confidence=1.0 - (diff_pct / 100),
                difference_percent=diff_pct,
                status=status,
                notes=f"Type match: {site_m['type']}"
            )
            
            self.matches.append(match)
            matched_site.append(site_m)
            matched_pdf.append(best_pdf)
            
            self.logger.info(f"   ✅ Matched: {site_m['type']} → {status} ({diff_pct:.1f}% diff)")
        
        # Remove matched measurements from unmatched lists
        for m in matched_site:
            self.unmatched_site.remove(m)
        for p in matched_pdf:
            self.unmatched_pdf.remove(p)
    
    def _match_by_proximity(self):
        """Pass 2: Match by spatial proximity (if location data available)"""
        self.logger.info("   📍 Pass 2: Matching by proximity...")
        
        # This requires location data (x, y coordinates) which may be available from YOLO
        # For now, this is a placeholder for future enhancement
        
        proximity_matches = 0
        for site_m in list(self.unmatched_site):
            # Would implement spatial matching here
            # Requires: site_m['x'], site_m['y'], pdf_m['x'], pdf_m['y']
            pass
        
        if proximity_matches > 0:
            self.logger.info(f"   ✅ Proximity matches: {proximity_matches}")
        else:
            self.logger.info(f"   ℹ️  No proximity matching (location data not available)")
    
    def _match_by_value(self):
        """Pass 3: Match by value similarity"""
        self.logger.info("   📍 Pass 3: Matching by value...")
        
        matched_site = []
        matched_pdf = []
        
        for site_m in list(self.unmatched_site):
            # Find all PDF measurements with similar value (within 30%)
            similar_pdf = [p for p in self.unmatched_pdf 
                          if abs(p['value_meters'] - site_m['value_meters']) / 
                             (site_m['value_meters'] or 1) < 0.30]
            
            if not similar_pdf:
                continue
            
            # Find closest match
            best_pdf = min(similar_pdf,
                          key=lambda p: abs(p['value_meters'] - site_m['value_meters']))
            
            diff_pct = abs(best_pdf['value_meters'] - site_m['value_meters']) / \
                      best_pdf['value_meters'] * 100 if best_pdf['value_meters'] != 0 else 0
            
            # Determine status
            if diff_pct <= self.MATCH_THRESHOLD * 100:
                status = 'match'
            elif diff_pct <= self.ISSUE_THRESHOLD * 100:
                status = 'issue'
            else:
                status = 'problem'
            
            # Create match with lower confidence (value-based, not type-based)
            match = ElementMatch(
                site_measurement=site_m,
                pdf_measurement=best_pdf,
                match_type='value_similarity',
                confidence=0.7 * (1.0 - (diff_pct / 100)),  # Lower base confidence
                difference_percent=diff_pct,
                status=status,
                notes=f"Value match: {site_m['value']}{site_m['unit']} ≈ {best_pdf['value']}{best_pdf['unit']}"
            )
            
            self.matches.append(match)
            matched_site.append(site_m)
            matched_pdf.append(best_pdf)
            
            self.logger.info(f"   ⚠️  Inferred match: {site_m['type']} → {best_pdf['type']} ({diff_pct:.1f}% diff)")
        
        # Remove matched from unmatched lists
        for m in matched_site:
            self.unmatched_site.remove(m)
        for p in matched_pdf:
            self.unmatched_pdf.remove(p)
    
    def detect_anomalies(self) -> Dict:
        """
        Detect measurement anomalies (missing, extra, mismatch)
        
        Returns:
            Dictionary with anomaly statistics
        """
        self.logger.info("🔍 Detecting anomalies...")
        
        anomalies = {
            'missing_in_site': [],  # Measurements in PDF not found on site
            'extra_in_site': [],    # Measurements on site not in PDF
            'mismatches': [],       # Significant differences
            'summary': {}
        }
        
        # Unmatched PDF measurements (should be on site but aren't)
        for pdf_m in self.unmatched_pdf:
            anomalies['missing_in_site'].append({
                'type': pdf_m['type'],
                'value': pdf_m['value'],
                'unit': pdf_m['unit'],
                'severity': 'high'
            })
            self.logger.warning(f"🚨 Missing in site: {pdf_m['type']} = {pdf_m['value']}{pdf_m['unit']}")
        
        # Unmatched site measurements (shouldn't be there)
        for site_m in self.unmatched_site:
            anomalies['extra_in_site'].append({
                'type': site_m['type'],
                'value': site_m['value'],
                'unit': site_m['unit'],
                'severity': 'medium'
            })
            self.logger.warning(f"⚠️  Extra in site: {site_m['type']} = {site_m['value']}{site_m['unit']}")
        
        # Significant mismatches
        for match in self.matches:
            if match.status == 'problem':
                anomalies['mismatches'].append({
                    'site': f"{match.site_measurement['value']}{match.site_measurement['unit']}",
                    'pdf': f"{match.pdf_measurement['value']}{match.pdf_measurement['unit']}",
                    'difference_percent': match.difference_percent,
                    'severity': 'high'
                })
                self.logger.error(f"🚨 Mismatch: {match.difference_percent:.1f}% difference")
        
        # Summary
        anomalies['summary'] = {
            'total_matches': len(self.matches),
            'missing_count': len(anomalies['missing_in_site']),
            'extra_count': len(anomalies['extra_in_site']),
            'mismatch_count': len(anomalies['mismatches']),
            'match_rate_percent': (len(self.matches) / (len(self.matches) + len(self.unmatched_pdf))) * 100
                                 if (len(self.matches) + len(self.unmatched_pdf)) > 0 else 0
        }
        
        self.logger.info(f"✅ Anomaly detection complete: "
                        f"{anomalies['summary']['missing_count']} missing, "
                        f"{anomalies['summary']['extra_count']} extra, "
                        f"{anomalies['summary']['mismatch_count']} mismatches")
        
        return anomalies
    
    def get_element_relationships(self) -> Dict:
        """
        Infer relationships between measurements
        
        Examples:
        - Width + Height = Area
        - Length + Width = Perimeter
        - Multiple measurements at same location = Same element
        
        Returns:
            Dictionary of inferred relationships
        """
        self.logger.info("🔗 Analyzing element relationships...")
        
        relationships = {
            'groups': [],           # Measurements of same element
            'sequences': [],        # Ordered dimensions
            'correlations': []      # Related measurements
        }
        
        # Group measurements by type and proximity
        for match in self.matches:
            site = match.site_measurement
            pdf = match.pdf_measurement
            
            # Check if this could be part of a sequence (L, W, H for a box)
            dimensional_types = ['length', 'width', 'height', 'depth']
            if any(t in site['type'] for t in dimensional_types):
                # Could be part of same element dimensions
                relationships['sequences'].append({
                    'site': site['type'],
                    'pdf': pdf['type'],
                    'match': match.match_type
                })
        
        self.logger.info(f"✅ Found {len(relationships['sequences'])} potential element relationships")
        
        return relationships
    
    def generate_match_report(self) -> Dict:
        """Generate comprehensive matching report"""
        self.logger.info("📊 Generating match report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_matches': len(self.matches),
                'matched_site': len([m for m in self.matches]),
                'unmatched_site': len(self.unmatched_site),
                'unmatched_pdf': len(self.unmatched_pdf)
            },
            'breakdown': {
                'exact_matches': len([m for m in self.matches if m.match_type == 'exact_type']),
                'inferred_matches': len([m for m in self.matches if m.match_type == 'value_similarity']),
                'status_match': len([m for m in self.matches if m.status == 'match']),
                'status_issue': len([m for m in self.matches if m.status == 'issue']),
                'status_problem': len([m for m in self.matches if m.status == 'problem'])
            },
            'anomalies': self.detect_anomalies(),
            'matches': [
                {
                    'site': {
                        'type': m.site_measurement['type'],
                        'value': m.site_measurement['value'],
                        'unit': m.site_measurement['unit'],
                        'value_m': m.site_measurement['value_meters']
                    },
                    'pdf': {
                        'type': m.pdf_measurement['type'],
                        'value': m.pdf_measurement['value'],
                        'unit': m.pdf_measurement['unit'],
                        'value_m': m.pdf_measurement['value_meters']
                    },
                    'match_type': m.match_type,
                    'confidence': m.confidence,
                    'difference_percent': m.difference_percent,
                    'status': m.status,
                    'notes': m.notes
                }
                for m in self.matches
            ]
        }
        
        self.logger.info(f"✅ Report generated: {report['summary']['total_matches']} matches")
        return report
    
    def save_report(self, report: Dict, output_path: str):
        """Save matching report to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"✅ Report saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save report: {e}")
    
    def get_statistics(self) -> Dict:
        """Get matching statistics"""
        if not self.matches:
            return {'error': 'No matches available'}
        
        values = [m.difference_percent for m in self.matches]
        confidences = [m.confidence for m in self.matches]
        
        return {
            'total_matches': len(self.matches),
            'average_difference': np.mean(values),
            'median_difference': np.median(values),
            'min_difference': np.min(values),
            'max_difference': np.max(values),
            'std_deviation': np.std(values),
            'average_confidence': np.mean(confidences),
            'median_confidence': np.median(confidences),
            'match_success_rate': len([m for m in self.matches if m.status == 'match']) / len(self.matches)
        }


# Standalone functions
def match_measurements(site_measurements: List[Dict], 
                      pdf_measurements: List[Dict],
                      logger: logging.Logger = None) -> List[ElementMatch]:
    """Convenience function to match measurements"""
    matcher = ElementMatcher(logger)
    return matcher.match_measurements(site_measurements, pdf_measurements)

def generate_report(site_measurements: List[Dict],
                   pdf_measurements: List[Dict],
                   output_path: str = None,
                   logger: logging.Logger = None) -> Dict:
    """Convenience function to generate match report"""
    matcher = ElementMatcher(logger)
    matcher.match_measurements(site_measurements, pdf_measurements)
    report = matcher.generate_match_report()
    
    if output_path:
        matcher.save_report(report, output_path)
    
    return report
