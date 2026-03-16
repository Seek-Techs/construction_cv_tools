from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract
import pandas as pd
import os
from utils import load_config, setup_logging, create_output_dir

class PDFProcessor:
    def __init__(self, config):
        self.config = config
        self.logger = setup_logging(config['log_level'])
        create_output_dir(config['output_dir'])

    def convert_pdf_to_images(self):
        try:
            pages = convert_from_path(self.config['pdf_path'])
            image_paths = []
            for i, page in enumerate(pages):
                path = f"{self.config['output_dir']}/page_{i+1}.jpg"
                page.save(path, 'JPEG')
                image_paths.append(path)
            self.logger.info(f"Converted {len(pages)} pages to images.")
            return image_paths
        except Exception as e:
            self.logger.error(f"PDF conversion failed: {e}")
            return []

    def detect_lines(self, image_path):
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            output_path = f"{self.config['output_dir']}/lines_{os.path.basename(image_path)}"
            cv2.imwrite(output_path, img)
            self.logger.info(f"Detected lines in {image_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Line detection failed for {image_path}: {e}")
            return None

    def read_measurements(self, image_path):
        try:
            img = cv2.imread(image_path)
            text = pytesseract.image_to_string(img, lang=self.config['ocr_lang'])
            self.logger.info(f"OCR text from {image_path}: {text[:100]}...")  # Short preview
            return text
        except Exception as e:
            self.logger.error(f"OCR failed for {image_path}: {e}")
            return ""

    def calculate_quantities(self, measurements):
        try:
            # Parse example: Find numbers (pro: Use regex for real)
            import re
            nums = re.findall(r'\d+\.?\d*', measurements)  # Find floats/ints
            if len(nums) >= 3:
                length, width, height = float(nums[0]), float(nums[1]), float(nums[2])
                area = length * width
                volume = area * height
                data = {'Item': ['Area', 'Volume'], 'Quantity': [area, volume]}
                df = pd.DataFrame(data)
                csv_path = f"{self.config['output_dir']}/quantities.csv"
                df.to_csv(csv_path, index=False)
                self.logger.info(f"Quantities saved to {csv_path}")
                return csv_path
            else:
                self.logger.warning("Not enough numbers for calc")
                return None
        except Exception as e:
            self.logger.error(f"Calculation failed: {e}")
            return None

    def detect_elements(self, image_path):
        results = self.model(image_path)  # self.model = YOLO(config['yolo_model'])
        # Save or process boxes for quantities