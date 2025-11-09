# detect.py
# for detection / inference

from ultralytics import YOLO
import cv2
from utils.lookup_table import get_carbon_value

# Load trained model (replace once downloaded)
model_path = "models/eco_model.pt"
model = YOLO(model_path)

# Run inference on a sample image
image_path = "dataset/images/sample.jpg"
results = model(image_path)

# Display detections and calculate CO₂ impact
total_co2 = 0

for r in results:
    boxes = r.boxes
    names = r.names
    for box in boxes:
        cls_id = int(box.cls[0])
        label = names[cls_id]
        co2 = get_carbon_value(label)
        total_co2 += co2
        print(f"Detected: {label} | CO₂: {co2} kg")

print(f"\nEstimated total environmental impact: {total_co2:.2f} kg CO₂")

# Show annotated image
results[0].show()
