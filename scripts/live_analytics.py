from ultralytics import YOLO
import cv2
from utils.lookup_table import get_carbon_value
from utils.biodegradable_lookup import is_biodegradable
from utils.database import create_table, log_detection

# Initialize database table
create_table()

# Load YOLOv11 trained model
model = YOLO("runs/eco_model2/weights/best.pt")

# Initialize stats
total_counts = {}
total_co2 = 0.0
total_biodegradable = 0
total_non_biodegradable = 0
frame_id = 0

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    frame_counts = {}
    frame_co2 = 0.0

    # Run detection
    results = model.predict(frame, imgsz=640, device="cpu")  # Use "cuda" if GPU is available

    for pred in results[0].boxes.data.tolist():
        x1, y1, x2, y2, conf, cls_id = pred
        cls_id = int(cls_id)
        cls_name = model.names[cls_id]

        # Update counts
        frame_counts[cls_name] = frame_counts.get(cls_name, 0) + 1
        total_counts[cls_name] = total_counts.get(cls_name, 0) + 1

        # CO2 calculation
        co2_value = get_carbon_value(cls_name)
        frame_co2 += co2_value
        total_co2 += co2_value

        # Biodegradable check
        biodegradable = is_biodegradable(cls_name)
        if biodegradable:
            total_biodegradable += 1
        else:
            total_non_biodegradable += 1

        # Draw bounding box and label
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f"{cls_name} {conf:.2f} CO2:{co2_value}",
                    (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        # Log detection in SQLite
        log_detection(cls_name, co2_value, biodegradable, conf, frame_id)

    # Display frame
    cv2.imshow("EcoVision Live Analytics", frame)

    # Console summary
    if frame_counts:
        print(f"Frame {frame_id} Counts: {frame_counts}")
        print(f"Frame CO2: {frame_co2:.2f} kg")
        print(f"Total CO2 so far: {total_co2:.2f} kg")
        print(f"Biodegradable: {total_biodegradable}, Non-biodegradable: {total_non_biodegradable}")
        print("-----")

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
