from ultralytics import YOLO
import cv2  # for showing image if needed
from utils import load_config, setup_logging

config = load_config()
logger = setup_logging(config['log_level'])

# Load your custom model
model = YOLO(config['yolo_model'])  # or config['yolo_model'] if loading from config

# Test on one image (change path to your PDF page or site photo)
image_path = r"C:\Users\Admin\Documents\Python project\2026\construction_cv_tool\As Built Drg.pdf"  # example from earlier PDF conversion
# or "site_photo.jpg" for a real site image with tape/brick

results = model(image_path)  # runs inference

# Print detections
print("Detected objects:")
for r in results:
    boxes = r.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        class_name = model.names[cls]  # e.g., 'reference_scale', 'circle_tank'
        print(f"- {class_name} | Confidence: {conf:.2f}")

# Show annotated image (optional)
annotated_img = results[0].plot()  # draws boxes
cv2.imwrite("annotated_test.jpg", annotated_img)
print("Saved annotated image as annotated_test.jpg")
cv2.imshow("Detections", annotated_img)
cv2.waitKey(0)
cv2.destroyAllWindows()