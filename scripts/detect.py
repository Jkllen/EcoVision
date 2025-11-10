import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
    results = model.predict(frame, imgsz=640, device="cpu")  # Use "cuda" if GPU available

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

    # ----- Overlay analytics on frame -----
    start_x, start_y = 10, 10
    line_height = 20
    max_bar_length = 150

    # Display total CO2
    cv2.putText(frame, f"Total CO2: {total_co2:.2f} kg", (start_x, start_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # Display biodegradable vs non-biodegradable
    cv2.putText(frame, f"Biodegradable: {total_biodegradable} | Non-biodegradable: {total_non_biodegradable}",
                (start_x, start_y + line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)

    # Display counts per material with color-coded bars
    bar_start_y = start_y + 2 * line_height
    for i, (mat, count) in enumerate(total_counts.items()):
        y_pos = bar_start_y + i * line_height
        bar_length = min(count * 10, max_bar_length)  # scale for display
        
        # Choose color: green for biodegradable, red for non-biodegradable
        if is_biodegradable(mat):
            color = (0, 255, 0)  # green
        else:
            color = (0, 0, 255)  # red
        
        # Draw text and bar
        cv2.putText(frame, f"{mat}: {count}", (start_x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.rectangle(frame, (start_x + 80, y_pos - 12), (start_x + 80 + int(bar_length), y_pos - 2), color, -1)


    # -------------------------------

    # Display frame
    cv2.imshow("EcoVision Live Analytics", frame)

    # Console summary
    if frame_counts:
        print(f"Frame {frame_id} Counts: {frame_counts}")
        print(f"Frame CO2: {frame_co2:.2f} kg")
        print(f"Total CO2 so far: {total_co2:.2f} kg")
        print(f"Biodegradable: {total_biodegradable}, Non-biodegradable: {total_non_biodegradable}")
        print("-----")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
