import sys, os
import threading
import time
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ultralytics import YOLO
from utils.lookup_table import get_carbon_value
from utils.biodegradable_lookup import is_biodegradable
from utils.database import create_table, log_detection

# ----------------- Recommended Actions -----------------
RECOMMENDATIONS = {
    "plastic": "Dispose in recycling bin (if labeled PET/HDPE). Avoid burning.",
    "paper": "Compost or recycle if clean and dry.",
    "metal": "Recycle at a scrap facility.",
    "glass": "Rinse and place in glass recycling bin.",
    "trash": "Send to landfill or waste facility.",
    "cardboard": "Flatten and recycle if not contaminated."
}

# ----------------- Initialize -----------------
create_table()
model = YOLO("../runs/eco_model2/weights/best.pt")

# Stats
total_counts = {}
total_co2 = 0.0
total_biodegradable = 0
total_non_biodegradable = 0
frame_id = 0

# ----------------- Threaded Camera Capture -----------------
class VideoStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy() if self.ret else None

    def release(self):
        self.stopped = True
        self.cap.release()

vs = VideoStream()

# ----------------- Tkinter GUI -----------------
root = tk.Tk()
root.title("EcoVision Dashboard")

# Frames
camera_frame = tk.Frame(root)
camera_frame.pack(side="left")
chart_frame = tk.Frame(root)
chart_frame.pack(side="right", fill="both", expand=True)

camera_label = tk.Label(camera_frame)
camera_label.pack()

fig = Figure(figsize=(4,3))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().pack()

# Recommendation history Text widget + scrollbar
rec_frame = tk.Frame(chart_frame)
rec_frame.pack(pady=10, fill="both")

rec_scrollbar = tk.Scrollbar(rec_frame)
rec_scrollbar.pack(side="right", fill="y")

rec_history = tk.Text(rec_frame, height=5, width=40, yscrollcommand=rec_scrollbar.set)
rec_history.pack(side="left", fill="both")
rec_history.configure(state='disabled')  # read-only
rec_scrollbar.config(command=rec_history.yview)

# ----------------- Recommendation History Management -----------------
MAX_HISTORY = 5
recommendation_list = []

def add_recommendation(text):
    global recommendation_list
    if not text:
        return
    recommendation_list.insert(0, text)  # newest on top
    if len(recommendation_list) > MAX_HISTORY:
        recommendation_list = recommendation_list[:MAX_HISTORY]

    rec_history.configure(state='normal')
    rec_history.delete(1.0, tk.END)
    for rec in recommendation_list:
        rec_history.insert(tk.END, rec + "\n")
    rec_history.configure(state='disabled')

# ----------------- Dashboard updater -----------------
def update_dashboard():
    while True:
        ax.clear()
        if total_counts:
            materials = list(total_counts.keys())
            co2_values = [get_carbon_value(m) * total_counts[m] for m in materials]
            colors = ['green' if is_biodegradable(m) else 'red' for m in materials]
            ax.bar(materials, co2_values, color=colors)
            ax.set_ylabel("CO₂ (kg)")
            ax.set_title(f"Total CO₂: {total_co2:.2f} | Biodegradable: {total_biodegradable} | Non-biodegradable: {total_non_biodegradable}")
        canvas.draw()
        time.sleep(1)

threading.Thread(target=update_dashboard, daemon=True).start()

# ----------------- Detection Loop -----------------
SKIP_FRAMES = 1  # detect every 2 frames (adjust for smoother CPU. For better camera feed, make it 1)
detect_counter = 0

def process_frame():
    global frame_id, total_co2, total_biodegradable, total_non_biodegradable, detect_counter
    ret, frame = vs.read()
    if ret:
        frame_id += 1
        detect_counter += 1
        frame_counts = {}
        frame_co2 = 0.0

        # Only run detection every SKIP_FRAMES
        if detect_counter >= SKIP_FRAMES:
            detect_counter = 0
            results = model.predict(frame, imgsz=512, device="cpu", conf=0.6)  # smaller size for faster CPU detection
            
            CONF_THRESHOLD = 0.6
            valid_preds = [pred for pred in results[0].boxes.data.tolist() if pred[4] >= CONF_THRESHOLD]
             
            if valid_preds:
                recommended_text = ""
                for pred in valid_preds:
                    x1, y1, x2, y2, conf, cls_id = pred
                    cls_id = int(cls_id)
                    cls_name = model.names[cls_id]

                    # Stats
                    frame_counts[cls_name] = frame_counts.get(cls_name, 0) + 1
                    total_counts[cls_name] = total_counts.get(cls_name, 0) + 1

                    co2_value = get_carbon_value(cls_name)
                    frame_co2 += co2_value
                    total_co2 += co2_value

                    biodegradable = is_biodegradable(cls_name)
                    if biodegradable:
                        total_biodegradable += 1
                    else:
                        total_non_biodegradable += 1

                    # Draw bounding box and label
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
                    cv2.putText(frame, f"{cls_name} {conf:.2f} CO2:{co2_value}", (int(x1), int(y1)-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

                    if not recommended_text:
                        recommended_text = RECOMMENDATIONS.get(cls_name, "Handle according to local rules")
                    log_detection(cls_name, co2_value, biodegradable, conf, frame_id)
            else:
                recommended_text = "Idle"
        # Update recommendation label
        root.after(0, lambda: add_recommendation(recommended_text))

        # Convert frame to Tkinter image
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

    camera_label.after(10, process_frame)

process_frame()
root.mainloop()
vs.release()
