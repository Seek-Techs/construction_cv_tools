# Construction CV Inspector

**A free, open-source computer vision tool for automated construction site inspection and verification**

## 🎯 Quick Summary

Construction CV Inspector helps small and medium construction teams **automatically compare real construction sites with architectural drawings** to find mistakes faster and resolve contractor disputes objectively.

**In simple terms:**
- You give it a PDF blueprint
- You take photos of the actual construction site
- It tells you what matches ✅, what's slightly off ⚠️, and what's seriously wrong 🚨

**Who it's for:** Small contractors, site engineers, quantity surveyors in Nigeria (especially Lagos) who want quality inspections without paying for expensive software.

---

## 🚀 What It Currently Does

✅ = Working now | ⚠️ = Partially working | ❌ = Not yet ready

| Feature | Status | What it does |
|---------|--------|-------------|
| PDF Processing | ✅ | Converts blueprints to images, detects lines/shapes, reads text with OCR |
| Object Detection | ✅ | Uses AI to find walls, tanks, pipes, bricks, tape measures in photos |
| YOLO Integration | ✅ | Custom-trained model for construction-specific objects |
| Scale Calibration | ⚠️ | Manual pixel-to-meter conversion (needs automation) |
| Measurement Extraction | ⚠️ | Reads dimensions from PDF and photos (needs improvement) |
| Comparison | ⚠️ | Compares measurements (basic logic, needs refinement) |
| Reporting | ❌ | Not yet - needs custom report generator |
| Web Interface | ❌ | Not yet - currently command-line only |

---

## 📋 System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows, Linux, or macOS
- **RAM:** 4GB minimum (8GB recommended)
- **GPU:** Optional (NVIDIA GPU makes it much faster)
- **Tesseract OCR:** Required for text reading from PDFs

### Install Tesseract (Windows)
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH or configure in code

---

## 🔧 Installation

### 1. Clone or Download Project
```bash
cd construction_cv_tool
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Settings
Edit `config.yaml`:
```yaml
pdf_path: your_blueprint.pdf          # Path to your blueprint
output_dir: outputs                    # Where to save results
yolo_model: weights/v1/best.pt        # Your trained model
ocr_lang: eng                          # Language for OCR
log_level: INFO                        # Logging verbosity
```

---

## 💻 How to Use

### **Option 1: Command Line (Simple)**

```bash
# Test the YOLO model
python test_model.py

# Run full workflow
python main.py
```

### **Option 2: Code-Based (For Developers)**

**Step 1: Process PDF Blueprint**
```python
from pdf_processor import PDFProcessor
from utils import load_config, setup_logging

config = load_config()
logger = setup_logging()

pdf_proc = PDFProcessor(config)
images = pdf_proc.convert_pdf_to_images()  # PDF → Images

for img in images:
    measurements = pdf_proc.read_measurements(img)  # Read text/dimensions
    print(f"Found measurements: {measurements}")
```

**Step 2: Analyze Site Photo**
```python
from site_comparator import SiteComparator

comparator = SiteComparator(config, logger)
result = comparator.compare_site_photo('path/to/site_photo.jpg', pdf_length=10.0)
print(f"Result: {result}")  # "Match" or "Mismatch" or "No detection"
```

**Step 3: Generate Report**
*(Coming soon in Phase 4)*

---

## 📁 Project Structure

```
construction_cv_tool/
│
├── main.py                          # Main workflow (start here)
├── pdf_processor.py                 # Blueprint analysis
├── site_comparator.py               # Site photo analysis
├── utils.py                         # Helper functions
├── test_model.py                    # Test YOLO model
├── config.yaml                      # Configuration
├── requirements.txt                 # Python packages
│
├── best.pt                          # YOLO model (PyTorch)
├── best.onnx                        # YOLO model (ONNX format)
├── weights/v1/                      # Additional model weights
│
└── outputs/                         # Results (auto-created)
    ├── page_1.jpg                   # Converted PDF pages
    ├── quantities.csv               # Extracted measurements
    └── ...
```

---

## 🤖 YOLO Model Details

**Current Model:** `weights/v1/best.pt`

The model has been trained on construction site images to detect:
- **Construction objects:** walls, tanks, pipes, bricks
- **Reference scales:** tape measures, rulers
- **Structural elements:** columns, beams, etc.

**Test the model:**
```bash
python test_model.py
```

**See detected classes:**
```python
from ultralytics import YOLO
model = YOLO('weights/v1/best.pt')
print(model.names)  # All detectable classes
```

---

## 🔍 Input Requirements

### PDF Blueprint
- **Format:** PDF (standard architectural drawing)
- **Quality:** Clear, readable drawings
- **Dimensions:** Must include measurements/dimensions
- **Content:** Lines, shapes, text labels, dimension markers

**Recommended prep:**
- Use original PDF from architect (not photos of drawings)
- Ensure OCR-readable text for measurements
- Include scale reference (1:100, 1:50, etc.)

### Site Photos
- **Camera:** Any smartphone or digital camera
- **Lighting:** Good natural lighting (avoid shadows)
- **Content:** Clear view of the element being checked
- **Reference:** Include tape measure, brick, or ruler for scale
- **Format:** JPG, PNG (1080p or higher recommended)

**Best practices:**
- Take multiple angles of same element
- Include measuring tape in photo for scale
- Avoid extreme angles (shoot straight-on when possible)
- Include context (neighboring elements, markings)

---

## 📊 Output Results

### Current Output
```
Final result: Match          # or "Mismatch" or "No detection"
```

### Future Output (Phase 4+)
- ✅ Detailed comparison report (PDF)
- ✅ Measurements table (Excel/CSV)
- ✅ Annotated images with differences highlighted
- ✅ Category breakdown: Matches vs Issues vs Problems
- ✅ GPS/location data (if available)
- ✅ Inspector notes

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pytesseract'"
**Solution:**
```bash
pip install pytesseract
# Also install Tesseract OCR from system
```

### Problem: "Tesseract is not installed"
**Solution:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location
3. Or set path in Python:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Problem: "YOLO model not found"
**Solution:**
1. Check `config.yaml` has correct path to `best.pt`
2. Ensure weights are in: `weights/v1/best.pt`
3. Run: `python test_model.py` to verify model loads

### Problem: "No objects detected"
**Possible causes:**
- Model not trained on your construction type
- Photo quality too poor
- Objects too small/far away
- Wrong angle

**Solution:**
- Test with multiple photos
- Ensure reference scale (tape/brick) is visible
- Check image resolution

### Problem: "Slow performance"
**Solution:**
- Use GPU: Install CUDA for faster inference
- Reduce image size before processing
- Use batch processing for multiple photos

---

## 🔧 Configuration Options

Edit `config.yaml` to customize behavior:

```yaml
# Path to blueprint PDF
pdf_path: blueprint.pdf

# Where to save results
output_dir: outputs

# YOLO model path
yolo_model: weights/v1/best.pt

# OCR language (eng=English, yor=Yoruba, etc.)
ocr_lang: eng

# Logging level (DEBUG, INFO, WARNING, ERROR)
log_level: INFO

# Measurement tolerance (for future phases)
tolerance_small: 0.05          # 5% difference = small issue
tolerance_large: 0.15          # 15% difference = big problem

# Unit settings
unit_system: metric            # or imperial
default_unit: m                # meters
```

---

## 🚀 Advanced Usage

### Custom YOLO Model
If you trained your own YOLO model:
```python
from ultralytics import YOLO

# Load custom model
model = YOLO('path/to/your/trained_model.pt')

# Run inference
results = model('site_photo.jpg')

# Process results
for r in results:
    boxes = r.boxes
    for box in boxes:
        print(f"Detected: {model.names[int(box.cls[0])]}")
```

### Batch Processing
```python
import os
from site_comparator import SiteComparator

photo_dir = 'photos/'
comparator = SiteComparator(config, logger)

for photo in os.listdir(photo_dir):
    if photo.endswith('.jpg'):
        result = comparator.compare_site_photo(os.path.join(photo_dir, photo))
        print(f"{photo}: {result}")
```

### Custom OCR Settings
```python
import pytesseract

# For construction measurements (numbers, units)
custom_config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.mEL:""'
text = pytesseract.image_to_string(image, config=custom_config)
```

---

## 📚 Development Roadmap

**Current:** MVP with basic functionality  
**Next phases:**
1. Reference scale auto-detection (days 1-4)
2. Improved measurement extraction (days 5-9)
3. Smart comparison engine (days 10-13)
4. Professional report generation (days 14-16)
5. Web interface (days 17-23)
6. Testing & optimization (days 24-30)

See `PROJECT_PURPOSE_AND_ROADMAP.md` for detailed timeline.

---

## 🤝 Contributing

This is a free, open-source project. To contribute:

1. Fork or clone the repository
2. Create a feature branch
3. Make your improvements
4. Test thoroughly
5. Submit a pull request

**Areas needing help:**
- [ ] Reference scale detection
- [ ] Improved OCR for measurements
- [ ] Report generation
- [ ] Web interface
- [ ] Testing on real projects
- [ ] Documentation

---

## 📄 License

*(Add your license here - MIT, GPL, or other)*

---

## 💬 Support & Questions

For help:
1. Check `PROJECT_PURPOSE_AND_ROADMAP.md` for detailed architecture
2. Review docstrings in Python files
3. Run `python test_model.py` to verify setup
4. Check logs in `outputs/` directory

---

## 🎓 How to Replicate This Project

**For developers who want to build something similar:**

### Core Technologies
- **Python 3.8+** - Programming language
- **YOLOv8** (Ultralytics) - Object detection
- **OpenCV** - Image processing
- **Pytesseract** - OCR/text extraction
- **PDF2Image** - PDF conversion
- **Pandas** - Data handling

### Learning Path
1. Learn OpenCV basics (image processing)
2. Understand YOLO object detection
3. Learn OCR with Tesseract
4. Study PDF handling with pdfmium or pdf2image
5. Practice with small dataset
6. Gradually build each module

### Training Your Own YOLO Model
1. Collect 500+ labeled construction images
2. Use Roboflow or similar for annotation
3. Train with: `yolo detect train data=construction.yaml epochs=100`
4. Replace `weights/v1/best.pt` with your trained model
5. Test and refine

### Deployment Options
- **CLI Tool** - Command-line interface (current)
- **Web App** - Flask/Streamlit (planned)
- **Mobile App** - React Native/Flutter (future)
- **API** - REST API for integration (future)

---

## 📊 Performance Metrics

*(To be filled after Phase 6 - Testing & QA)*

- **Detection accuracy:** XX%
- **Measurement accuracy:** ±XX%
- **Processing speed:** XX seconds per photo
- **False positive rate:** XX%

---

**Last Updated:** February 15, 2026  
**Version:** 1.0 - MVP  
**Status:** Early development - use for testing/learning only  
**Next Milestone:** Phase 1 completion (Reference scale detection)

---

### Quick Links
- 📄 [Project Purpose & Roadmap](PROJECT_PURPOSE_AND_ROADMAP.md)
- 🔧 [Configuration Guide](#configuration-options)
- 🚀 [Development Roadmap](#-development-roadmap)
- 🤖 [YOLO Model Details](#-yolo-model-details)
