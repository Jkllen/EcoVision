from ultralytics import YOLO

# Load YOLOv11 model (pretrained backbone for transfer learning)
model = YOLO("yolov11n.pt")  # 'n' for nano, fast training; can also use 's', 'm', 'l'

# Train the model
model.train(
    data="../dataset/data.yaml",   # path to your exported data.yaml
    epochs=50,                     # adjust for your dataset size & GPU capacity
    imgsz=640,                     # image size
    batch=16,                      # batch size (adjust based on your GPU/CPU)
    project="../models",            # save results here
    name="eco_model",              # subfolder for this training run
    device=0                       # 0 = first GPU; "cpu" = CPU-only
)
