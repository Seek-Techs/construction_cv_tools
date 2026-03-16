from ultralytics import YOLO

model = YOLO(r"C:\Users\Admin\Documents\Python project\2026\construction_cv_tool\best.pt")

# Export to ONNX (good for cross-platform, faster CPU inference)
model.export(format="onnx", imgsz=640, dynamic=True)

# Export to TFLite (for mobile/Android apps later)
model.export(format="tflite", imgsz=640)

# Or both at once
# model.export(format=["onnx", "tflite"])