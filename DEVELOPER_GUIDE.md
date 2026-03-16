# Construction CV Inspector - Developer's Implementation Guide

## 📖 Overview

This guide explains the current architecture, each module's purpose, and how to extend the project to achieve the full vision.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Construction CV Inspector                     │
└─────────────────────────────────────────────────────────────────┘

Input Layer:
├─ PDF Blueprint (PDF file)
└─ Site Photos (JPG/PNG)

Processing Pipeline:
├─ Module 1: PDF Processor
│  ├─ convert_pdf_to_images()    → Extract images from PDF
│  ├─ detect_lines()              → Find geometric shapes
│  └─ read_measurements()         → OCR to extract text/numbers
│
├─ Module 2: Site Comparator
│  ├─ detect_objects()            → YOLO inference on site photos
│  └─ compare_site_photo()        → Compare with PDF measurements
│
├─ Module 3: Reference Scale Detector (TODO)
│  ├─ detect_scale_reference()    → Find tape measure or brick
│  └─ calculate_scale()           → Convert pixels to real units
│
└─ Module 4: Report Generator (TODO)
   └─ generate_report()           → Create comparison report

Output Layer:
├─ CSV measurements
├─ Comparison results
└─ Report (PDF/Excel/JSON)
```

---

## 📦 Module Breakdown

### **1. pdf_processor.py** - Blueprint Analysis

**Purpose:** Convert PDF drawings to usable data

**Key Methods:**

#### `convert_pdf_to_images()`
- **Input:** PDF file path (from config)
- **Output:** List of image file paths (one per page)
- **How it works:**
  ```python
  pages = convert_from_path(pdf_path)      # Convert PDF to images
  for each page:
      save as JPG
      add to list
  return list
  ```
- **Status:** ✅ Working

#### `detect_lines(image_path)`
- **Input:** Image file path
- **Output:** Image with detected lines drawn on it
- **How it works:**
  ```python
  img = read_image()
  gray = convert_to_grayscale()
  edges = find_edges_using_Canny()        # Edge detection
  lines = find_lines_using_HoughLP()     # Line detection
  draw_lines_on_image()
  save_result()
  ```
- **Status:** ✅ Working (basic)
- **Needs improvement:** Better edge detection, noise handling

#### `read_measurements(image_path)`
- **Input:** Image of blueprint page
- **Output:** Raw text extracted from image
- **How it works:**
  ```python
  img = read_image()
  text = pytesseract.image_to_string(img)  # OCR
  return text
  ```
- **Status:** ⚠️ Working but crude
- **Needs improvement:**
  - Preprocess image (contrast, blur) before OCR
  - Parse output to extract numbers, units, dimensions
  - Regex patterns: `10.5m`, `EL:102.550`, `24"`, `Ø 300mm`

#### `calculate_quantities(measurements)`
- **Input:** Raw OCR text or measurement string
- **Output:** CSV file with extracted quantities
- **How it works:**
  ```python
  parse measurements = extract_numbers(text)
  calculate area = length × width
  calculate volume = area × height
  save_to_csv()
  ```
- **Status:** ⚠️ Basic implementation (too simple)
- **Needs improvement:**
  - Better parsing of measurement formats
  - Support multiple measurement types
  - Organize by element (wall 1, tank 2, etc.)

---

### **2. site_comparator.py** - Site Photo Analysis

**Purpose:** Analyze real site photos and compare with blueprint

**Key Methods:**

#### `__init__(config, logger)`
- Load YOLO model specified in config
- Initialize logging
- **Status:** ✅ Working

#### `compare_site_photo(photo_path, pdf_length)`
- **Input:**
  - `photo_path`: Path to site photo
  - `pdf_length`: Known dimension from PDF (e.g., 10.0m)
- **Output:** String result - "Match", "Mismatch", "No detection", or "Error"
- **How it works:**
  ```python
  img = read_image(photo_path)
  results = yolo_model(img)                  # Run YOLO inference
  boxes = extract_bounding_boxes(results)
  if boxes detected:
      real_width = boxes[0].width            # In pixels
      site_length = real_width / scale       # Convert to meters
      difference = abs(pdf_length - site_length)
      if difference < threshold:
          return "Match"
      else:
          return "Mismatch"
  else:
      return "No detection"
  ```
- **Status:** ⚠️ Working but simplistic
- **Problems:**
  - Hard-coded scale (real_width / 100.0) - doesn't work for different photos
  - Only compares first detected object
  - No reference scale detection
  - Can't handle multiple objects

---

### **3. config.yaml** - Configuration

**Purpose:** Store all settings without changing code

**Current settings:**
```yaml
pdf_path: blueprint.pdf
output_dir: outputs
yolo_model: weights/v1/best.pt
ocr_lang: eng
log_level: INFO
```

**Future settings (when implemented):**
```yaml
# Scale calibration
reference_scale_type: tape_measure  # or brick, ruler
scale_tolerance_px: 5               # ±5 pixels acceptable

# Measurement tolerance (Phase 3)
tolerance_small_percent: 0.05       # 5% = small issue
tolerance_large_percent: 0.15       # 15% = big problem

# Report settings (Phase 4)
report_format: pdf                  # or excel, json
include_images: true
include_measurements_table: true

# Web UI settings (Phase 5)
web_port: 5000
max_upload_size_mb: 100
temp_storage: temp/
```

---

### **4. utils.py** - Helper Functions

**Status:** ✅ Basic utilities working

**Current functions:**
- `setup_logging()` - Configure logging
- `load_config()` - Load YAML config
- `create_output_dir()` - Ensure output folder exists

**Needs expansion:**
- `extract_measurements_from_text()` - Parse OCR output
- `normalize_units()` - Convert to standard unit
- `calculate_percentage_diff()` - For Phase 3
- `create_annotated_image()` - Draw boxes/annotations
- `save_to_csv()` - Export measurements
- `save_to_json()` - Export structured data

---

## 🔄 Complete Workflow

### **Current Simple Workflow**

```
1. Load config
2. Setup logging
3. PDF Processor:
   - Convert PDF → Images
   - Detect lines
   - Read measurements via OCR
4. Site Comparator:
   - Load YOLO model
   - Run inference on site photo
   - Compare with PDF measurement
5. Output result (Match/Mismatch)
```

### **Complete Workflow (Target)**

```
1. Load & validate config

2. BLUEPRINT ANALYSIS:
   a. Convert PDF → Images per page
   b. For each page:
      - Detect line-based dimensions
      - Extract text measurements
      - Recognize symbols (circles, squares)
      - Parse all measurements
   c. Store in structured format:
      {
        "elements": [
          {"id": "wall_1", "type": "wall", "length": 10.5, "unit": "m"},
          {"id": "tank_1", "type": "tank", "diameter": 2.0, "unit": "m"}
        ]
      }

3. SITE PHOTO ANALYSIS:
   a. Detect reference scale (tape measure or brick)
   b. Calculate scale: pixels_per_meter
   c. Run YOLO detection
   d. For each detected object:
      - Get bounding box (pixels)
      - Convert to real dimensions (using scale)
      - Extract any visible measurements
   e. Store results:
      {
        "detections": [
          {"id": "wall_detected_1", "type": "wall", "length": 10.3, "unit": "m"}
        ]
      }

4. MATCHING & COMPARISON:
   a. Match PDF elements to site detections
      (by type, location, size similarity)
   b. For each match:
      - Calculate difference
      - Determine category (Match/Small Issue/Big Problem)
   c. Flag unmatched elements

5. REPORT GENERATION:
   a. Create summary:
      - ✅ 15 Matches
      - ⚠️ 3 Small Issues
      - 🚨 1 Big Problem
   b. Generate detailed table
   c. Create annotated images
   d. Export (PDF, Excel, JSON)

6. Output & logging
```

---

## 🚀 Phase-by-Phase Implementation

### **PHASE 1: Reference Scale Detection**

**Why:** Current hardcoded scale doesn't work for different photos/cameras

**Files to create:** `reference_scale_detector.py`

**What to implement:**

```python
class ReferenceScaleDetector:
    def __init__(self, yolo_model):
        self.model = yolo_model  # Reuse YOLO for scale detection
    
    def detect_tape_measure(self, image):
        """Detect tape measure in photo and return length in pixels"""
        # Run YOLO detection
        # Find object with class 'tape_measure'
        # Return bounding box width
        pass
    
    def detect_brick_reference(self, image):
        """Detect brick (standard brick = 19cm)"""
        # Find brick in image
        # Return size in pixels
        pass
    
    def calculate_scale(self, image):
        """Auto-calculate pixels per meter"""
        # Try tape measure first
        if tape_detected:
            tape_pixels = detect_tape_measure()  # Usually 1m or 3m
            tape_length_m = 1.0  # or 3.0 depending on tape
            return tape_pixels / tape_length_m
        
        # Fall back to brick
        if brick_detected:
            brick_pixels = detect_brick_reference()
            brick_length_m = 0.19  # Standard brick in meters
            return brick_pixels / brick_length_m
        
        # If nothing detected, ask user
        return None
    
    def validate_scale(self, scale):
        """Sanity check on scale"""
        # Scale should be reasonable (e.g., 100-1000 pixels/meter)
        # Detect if photo is too far or too close
        pass
```

**How to integrate:**

```python
# In site_comparator.py
from reference_scale_detector import ReferenceScaleDetector

class SiteComparator:
    def __init__(self, config, logger):
        self.scale_detector = ReferenceScaleDetector(self.model)
    
    def compare_site_photo(self, photo_path, pdf_length):
        img = cv2.imread(photo_path)
        scale = self.scale_detector.calculate_scale(img)  # NEW!
        
        if scale is None:
            logger.error("Could not detect reference scale")
            return "Error: No reference scale found"
        
        # Now use auto-detected scale instead of hardcoded
        results = self.model(img)
        # ... rest of comparison using scale
```

---

### **PHASE 2: Improved Measurement Extraction**

**Why:** Need accurate, parseable measurements from both PDF and photos

**Files to update:** `pdf_processor.py`, `utils.py`

**What to implement:**

**Improve OCR preprocessing:**

```python
def preprocess_for_ocr(image):
    """Enhance image for better OCR accuracy"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Sharpen
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return sharpened

def read_measurements_improved(image_path):
    """Extract measurements with parsing"""
    img = cv2.imread(image_path)
    preprocessed = preprocess_for_ocr(img)
    
    # Custom OCR config for construction measurements
    custom_config = r'--psm 6 --oem 3'
    text = pytesseract.image_to_string(preprocessed, config=custom_config)
    
    # Parse the text
    measurements = parse_measurements(text)
    return measurements
```

**Parse measurements:**

```python
import re

def parse_measurements(text):
    """Extract structured measurements from OCR text"""
    measurements = []
    
    # Regex patterns for common construction measurements
    patterns = {
        'meters': r'(\d+\.?\d*)\s*m(?:\s|$)',  # 10.5 m
        'elevation': r'EL:\s*(\d+\.?\d*)',      # EL: 102.550
        'diameter': r'[Ø∅]\s*(\d+\.?\d*)',      # Ø 300mm
        'inches': r'(\d+\.?\d*)\s*"',           # 24"
        'mm': r'(\d+\.?\d*)\s*mm',              # 150mm
    }
    
    for measurement_type, pattern in patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            measurements.append({
                'type': measurement_type,
                'value': float(match.group(1)),
                'raw': match.group(0)
            })
    
    return measurements

def normalize_to_meters(measurements):
    """Convert all to meters"""
    conversions = {
        'mm': 0.001,
        'inches': 0.0254,
    }
    
    for m in measurements:
        if m['type'] in conversions:
            m['value_m'] = m['value'] * conversions[m['type']]
        elif m['type'] == 'meters':
            m['value_m'] = m['value']
    
    return measurements
```

**Store structured data:**

```python
def save_measurements_json(measurements, output_path):
    """Save measurements in structured JSON format"""
    data = {
        'blueprint': {
            'elements': measurements,
            'total_measurements': len(measurements),
            'timestamp': datetime.now().isoformat()
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
```

---

### **PHASE 3: Smart Comparison & Matching**

**Why:** Need to intelligently match PDF elements to site detections

**Files to create:** `element_matcher.py`

**What to implement:**

```python
class ElementMatcher:
    def __init__(self, tolerance=0.15):
        self.tolerance = tolerance  # 15% difference threshold
    
    def match_elements(self, pdf_measurements, site_measurements):
        """Match PDF elements to site detected elements"""
        matches = []
        unmatched_pdf = list(pdf_measurements)
        unmatched_site = list(site_measurements)
        
        for pdf_elem in pdf_measurements:
            best_match = None
            best_score = 0
            
            for site_elem in site_measurements:
                # Calculate similarity score
                score = self.calculate_similarity(pdf_elem, site_elem)
                
                if score > best_score and score > 0.7:  # 70% minimum similarity
                    best_score = score
                    best_match = site_elem
            
            if best_match:
                matches.append({
                    'pdf': pdf_elem,
                    'site': best_match,
                    'similarity': best_score
                })
                unmatched_pdf.remove(pdf_elem)
                unmatched_site.remove(best_match)
        
        return {
            'matches': matches,
            'unmatched_pdf': unmatched_pdf,
            'unmatched_site': unmatched_site
        }
    
    def calculate_similarity(self, elem1, elem2):
        """Calculate how similar two elements are"""
        score = 0
        
        # Type matching (most important)
        if elem1.get('type') == elem2.get('type'):
            score += 0.5
        
        # Size matching
        size_diff = abs(elem1['size'] - elem2['size']) / elem1['size']
        if size_diff < 0.1:  # Within 10%
            score += 0.3
        elif size_diff < 0.2:
            score += 0.15
        
        # Location proximity (if coordinates available)
        if 'location' in elem1 and 'location' in elem2:
            dist = self.calculate_distance(elem1['location'], elem2['location'])
            if dist < 100:  # Pixels
                score += 0.2
        
        return score
    
    def categorize_difference(self, pdf_value, site_value):
        """Categorize measurement difference"""
        diff_percent = abs(pdf_value - site_value) / pdf_value * 100
        
        if diff_percent < 5:
            return ('match', '✅ MATCH')
        elif diff_percent < 15:
            return ('small_issue', '⚠️ SMALL DIFFERENCE')
        else:
            return ('big_problem', '🚨 BIG PROBLEM')
    
    def generate_comparison_summary(self, matches):
        """Create summary statistics"""
        summary = {
            'total_comparisons': len(matches),
            'matches': 0,
            'small_issues': 0,
            'big_problems': 0,
            'details': []
        }
        
        for match in matches:
            pdf_val = match['pdf']['value']
            site_val = match['site']['value']
            
            category, label = self.categorize_difference(pdf_val, site_val)
            
            summary[category] += 1
            summary['details'].append({
                'element': match['pdf'].get('id', 'unknown'),
                'pdf_value': pdf_val,
                'site_value': site_val,
                'difference_percent': ((site_val - pdf_val) / pdf_val * 100),
                'category': label
            })
        
        return summary
```

---

### **PHASE 4: Report Generation**

**Why:** Output needs to be understood by non-technical stakeholders

**Files to create:** `report_generator.py`

**What to implement:**

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

class ReportGenerator:
    def __init__(self, output_dir='reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_pdf_report(self, comparison_summary, annotated_images, output_file):
        """Generate professional PDF report"""
        doc = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []
        
        # Header
        elements.append(Paragraph("CONSTRUCTION SITE INSPECTION REPORT", style=title_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Summary section
        summary_data = [
            ['Category', 'Count'],
            ['✅ Matches', str(comparison_summary['matches'])],
            ['⚠️ Small Issues', str(comparison_summary['small_issues'])],
            ['🚨 Big Problems', str(comparison_summary['big_problems'])]
        ]
        summary_table = Table(summary_data)
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed comparison table
        detail_data = [['Element', 'PDF Value', 'Site Value', 'Difference', 'Status']]
        for detail in comparison_summary['details']:
            detail_data.append([
                detail['element'],
                f"{detail['pdf_value']:.2f}",
                f"{detail['site_value']:.2f}",
                f"{detail['difference_percent']:.1f}%",
                detail['category']
            ])
        detail_table = Table(detail_data)
        elements.append(detail_table)
        
        # Add annotated images
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("DETAILED ANALYSIS", style=heading_style))
        for img_path in annotated_images:
            elements.append(Image(img_path, width=5*inch, height=4*inch))
            elements.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(elements)
        print(f"Report saved to: {output_file}")
    
    def generate_excel_report(self, comparison_summary, output_file):
        """Generate Excel spreadsheet"""
        df = pd.DataFrame(comparison_summary['details'])
        df.to_excel(output_file, sheet_name='Comparison', index=False)
        print(f"Excel report saved to: {output_file}")
    
    def generate_json_report(self, comparison_summary, output_file):
        """Generate JSON for programmatic use"""
        with open(output_file, 'w') as f:
            json.dump(comparison_summary, f, indent=2)
        print(f"JSON report saved to: {output_file}")
```

---

### **PHASE 5: Web Interface**

**Why:** End users (contractors, supervisors) can't use command line

**Files to create:** `web_ui/app.py`, `web_ui/templates/`, `web_ui/static/`

**Basic structure:**

```python
from flask import Flask, render_template, request, send_file
from pdf_processor import PDFProcessor
from site_comparator import SiteComparator
from element_matcher import ElementMatcher
from report_generator import ReportGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

@app.route('/')
def upload():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
    pdf = request.files['pdf']
    photos = request.files.getlist('photos')
    
    # Save uploaded files
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
    pdf.save(pdf_path)
    
    photo_paths = []
    for photo in photos:
        path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        photo.save(path)
        photo_paths.append(path)
    
    # Process
    try:
        pdf_proc = PDFProcessor(config)
        pdf_measurements = pdf_proc.process_pdf(pdf_path)
        
        comparator = SiteComparator(config, logger)
        site_measurements = []
        for photo_path in photo_paths:
            site_measurements.extend(comparator.analyze_photo(photo_path))
        
        matcher = ElementMatcher()
        comparison = matcher.match_elements(pdf_measurements, site_measurements)
        summary = matcher.generate_comparison_summary(comparison['matches'])
        
        # Store results in session
        session['summary'] = summary
        
        return redirect(url_for('results'))
    
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/results')
def results():
    summary = session.get('summary', {})
    return render_template('results.html', summary=summary)

@app.route('/download_report')
def download_report():
    summary = session.get('summary', {})
    generator = ReportGenerator()
    report_path = generator.generate_pdf_report(summary)
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 🧪 Testing Strategy

### **Unit Tests (for each module)**

```python
# tests/test_pdf_processor.py
import unittest
from pdf_processor import PDFProcessor

class TestPDFProcessor(unittest.TestCase):
    def test_convert_pdf_to_images(self):
        # Test PDF conversion
        pass
    
    def test_read_measurements_extraction(self):
        # Test OCR parsing
        pass
    
    def test_measurement_parsing(self):
        # Test regex extraction
        pass

# tests/test_site_comparator.py
class TestSiteComparator(unittest.TestCase):
    def test_yolo_inference(self):
        # Test model loads and runs
        pass
    
    def test_scale_detection(self):
        # Test reference scale detection
        pass

# tests/test_element_matcher.py
class TestElementMatcher(unittest.TestCase):
    def test_element_matching(self):
        # Test matching algorithm
        pass
    
    def test_difference_categorization(self):
        # Test Match/Issue/Problem categorization
        pass
```

### **Integration Tests**

```python
# tests/test_full_workflow.py
def test_complete_workflow():
    """Test from PDF to final report"""
    pdf_path = 'test_data/blueprint.pdf'
    photo_path = 'test_data/site_photo.jpg'
    
    # Process PDF
    pdf_proc = PDFProcessor(config)
    pdf_measurements = pdf_proc.process_pdf(pdf_path)
    
    # Process site photo
    comparator = SiteComparator(config, logger)
    site_measurements = comparator.analyze_photo(photo_path)
    
    # Compare
    matcher = ElementMatcher()
    summary = matcher.generate_comparison_summary(
        matcher.match_elements(pdf_measurements, site_measurements)
    )
    
    # Generate report
    generator = ReportGenerator()
    report_path = generator.generate_pdf_report(summary)
    
    assert os.path.exists(report_path)
```

### **Real-World Testing**

- [ ] Test with 20+ real construction site photos
- [ ] Test with different PDF formats
- [ ] Test with different camera models/angles
- [ ] Test in different lighting conditions
- [ ] Measure accuracy vs manual measurements
- [ ] Get user feedback

---

## 📈 Performance Optimization Tips

1. **Faster YOLO inference:**
   - Use GPU (CUDA)
   - Reduce input image size
   - Batch multiple images

2. **Faster OCR:**
   - Preprocess images to reduce noise
   - Use Region-of-Interest (ROI) detection
   - Consider EasyOCR for some use cases

3. **Caching:**
   - Cache model after first load
   - Cache config file

4. **Parallelization:**
   - Process multiple photos in parallel
   - Process multiple PDF pages in parallel

---

## 🐛 Common Debugging Tips

**Model not loading:**
```python
from ultralytics import YOLO
try:
    model = YOLO(model_path)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
```

**OCR not working:**
```python
import pytesseract
try:
    text = pytesseract.image_to_string(image)
    print(f"✅ OCR successful: {text[:50]}")
except Exception as e:
    print(f"❌ Tesseract not found: {e}")
    print("Install from: https://github.com/UB-Mannheim/tesseract/wiki")
```

**No objects detected:**
```python
# Check model classes
from ultralytics import YOLO
model = YOLO('weights/v1/best.pt')
print("Model classes:", model.names)

# Test with different confidence threshold
results = model(image, conf=0.3)  # Lower threshold
```

---

## 🎓 Additional Resources

- **OpenCV:** https://docs.opencv.org/
- **YOLO/Ultralytics:** https://docs.ultralytics.com/
- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **Flask:** https://flask.palletsprojects.com/
- **Reportlab (PDF):** https://www.reportlab.com/docs/reportlab-userguide.pdf

---

**Last Updated:** February 15, 2026  
**Version:** 1.0 - Early Development
