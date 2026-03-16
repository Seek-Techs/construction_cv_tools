import logging
import yaml
import os
import re
import json
from datetime import datetime

def setup_logging(level='INFO'):
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    return logger

def load_config(config_path='config.yaml'):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def create_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def save_json(data, output_path):
    """Save data to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(input_path):
    """Load data from JSON file"""
    with open(input_path, 'r') as f:
        return json.load(f)

def normalize_units(value, from_unit, to_unit='m'):
    """
    Convert measurements to standard unit (meters)
    
    Supported units: mm, cm, m, inches, feet
    """
    unit_conversions = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'inches': 0.0254,
        'feet': 0.3048,
        '"': 0.0254,  # Inches symbol
    }
    
    if from_unit not in unit_conversions or to_unit not in unit_conversions:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")
    
    value_in_meters = value * unit_conversions[from_unit]
    value_in_target = value_in_meters / unit_conversions[to_unit]
    
    return value_in_target

def extract_measurements_from_text(text):
    """
    Extract measurements from OCR text
    
    Returns list of measurements with type and value
    """
    measurements = []
    
    patterns = {
        'meters': r'(\d+\.?\d*)\s*m(?:\s|$|\.)',
        'elevation': r'EL:\s*(\d+\.?\d*)',
        'diameter': r'[Ø∅]\s*(\d+\.?\d*)',
        'inches': r'(\d+\.?\d*)\s*"',
        'mm': r'(\d+\.?\d*)\s*mm',
        'cm': r'(\d+\.?\d*)\s*cm',
    }
    
    for measurement_type, pattern in patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            measurements.append({
                'type': measurement_type,
                'value': float(match.group(1)),
                'raw': match.group(0),
                'unit': 'm' if measurement_type == 'meters' else measurement_type
            })
    
    return measurements

def calculate_percentage_diff(value1, value2):
    """Calculate percentage difference between two values"""
    if value1 == 0:
        return None
    return abs(value2 - value1) / abs(value1) * 100

def categorize_difference(diff_percent, small_threshold=5, large_threshold=15):
    """
    Categorize measurement difference
    
    Args:
        diff_percent: Percentage difference
        small_threshold: Threshold for small issue (%)
        large_threshold: Threshold for big problem (%)
    
    Returns:
        Tuple: (category, label)
    """
    if diff_percent <= small_threshold:
        return ('match', '✅ MATCH')
    elif diff_percent <= large_threshold:
        return ('small_issue', '⚠️ SMALL ISSUE')
    else:
        return ('big_problem', '🚨 BIG PROBLEM')

def create_measurement_record(element_id, element_type, value, unit='m', source='unknown'):
    """Create standardized measurement record"""
    return {
        'id': element_id,
        'type': element_type,
        'value': value,
        'unit': unit,
        'source': source,
        'timestamp': datetime.now().isoformat()
    }

def validate_measurement(value, min_value=0.01, max_value=1000):
    """Validate that measurement is reasonable"""
    return min_value <= value <= max_value