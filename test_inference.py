# test_inference.py
from ultralytics import YOLO

model = YOLO(r"C:\Users\Admin\Documents\Python project\2026\construction_cv_tool\best.pt")  # path to your downloaded file

# Test on a single image
results = model(r"C:\Users\Admin\Documents\Python project\2026\construction_cv_tool\image.png")  # e.g., page_1.jpg or site_photo.jpg

# Show results
results[0].show()  # opens window with boxes

# Or save annotated image
results[0].save("annotated_test.jpg")