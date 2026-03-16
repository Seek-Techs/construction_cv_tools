# Custom Instructions for Construction CV Inspector Project

## Project Overview
This is a free, open-source Python computer vision tool for construction site inspections in Nigeria (Lagos focus).
- Analyzes PDF blueprints (quantity takeoff, lines, symbols, OCR dimensions)
- Detects & measures real elements from site photos using custom YOLO model
- Compares as-built (site) vs as-designed (blueprint) — flags mismatches
- Uses tape measure / brick as reference for real-world scaling
- Goal: affordable, customizable alternative to expensive tools like Togal.AI / Pix4D

## Tech Stack & Preferred Libraries
- Python 3.10+
- Core: opencv-python, ultralytics (YOLOv11+), pytesseract, pdf2image, pillow, numpy, pandas
- Logging: Python logging module (INFO level default)
- Config: YAML via pyyaml
- Testing: pytest when needed
- Avoid: deprecated code (e.g., old cv2 APIs), unnecessary dependencies
- Always prefer: type hints, docstrings, modular classes

## Coding Style & Conventions
- Follow PEP 8 + Black formatting style (line length 88–100)
- Use snake_case for variables/functions, CamelCase for classes
- Add docstrings (Google style) to every class/method/function
- Use f-strings for formatting
- Prefer pathlib over os.path
- Error handling: try/except with specific exceptions + logger.error
- Always log important steps (logger.info / warning / error)
- No print() for production code — use logging
- Keep functions short (<50 lines when possible)
- Modular: one responsibility per class/method
- Config-driven: load from config.yaml, never hard-code paths/values

## Project Structure Expectations
- main.py → entry point, orchestrates workflow
- pdf_processor.py → PDF → images → detection → OCR → quantities
- site_comparator.py → YOLO on site photo → scale calibration → comparison
- utils.py → helpers (logging setup, config load, dir creation)
- config.yaml → all paths, model, settings
- weights/ → best.pt and exports
- outputs/ → generated images, CSVs, reports

## When Generating / Editing Code
- Always respect existing modular structure — don't merge classes/files
- Use existing utils (setup_logging, load_config) when possible
- For YOLO: use ultralytics.YOLO, prefer yolo11s.pt / yolo11n.pt
- For OpenCV: cv2.imread, cv2.imwrite, Canny/Hough for lines
- For scaling: detect 'reference_scale' class → compute pixel-to-meter ratio
- Add comments explaining non-obvious logic (especially math/calibration)
- Suggest tests when adding new features
- Never remove logging or error handling

## Additional Rules
- Be concise but complete in suggestions
- If unsure about a decision, ask for clarification instead of assuming
- Prioritize safety/readability over clever one-liners
- Use modern Python (match typing, walrus operator if helpful)

Last updated: February 2026