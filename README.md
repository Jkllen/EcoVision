# EcoVision - LAN-based Waste Classification System

**EcoVision** is an intelligent waste classification system using computer vision and YOLOv11. It detects and categorizes waste (cardboard, glass, metal, paper, plastic, trash/biodegradable) from images or live video feed. The system integrates deep learning and preprocessing workflows for reliable and accurate waste recognition.

---

## 📁 Project Structure

```bash
C:.
│   ecovstructure.txt
│   README.md
│   requirements.txt
│   
├───dataset
├───models
├───scripts
│   │   detect.py
│   │   
│   └───__pycache__
│           lookup_table.cpython-313.pyc
│           
├───utils
│       lookup_table.py
│       
└───venv
    │   .gitignore
    │   pyvenv.cfg
    │   
    ├───Include
    ├───Lib               
    ├───Scripts           
    └───share
```               
---

- **dataset/** – Contains all images and annotations used for training and testing.  
- **models/** – Stores trained YOLOv11 weights and model checkpoints.  
- **scripts/** – Python scripts for detection and inference.  
  - `detect.py` – Run detection on images, videos, or webcam feed.  
- **utils/** – Utility scripts, e.g., `lookup_table.py` for mapping waste categories to properties like biodegradable or recyclable.  
- **venv/** – Python virtual environment with all dependencies installed.  
- **requirements.txt** – List of required Python packages.  
- **ecovstructure.txt** – structure reference.  

---

## ⚙️ Setup Instructions

1. **Clone the repository**  
```bash
   git clone <repo_url>
   cd EcoVision
```
2. **Create and Activate the Virtual Environment**
```bash
    python -m venv venv
    venv\Scripts\activate
```
3. **Install Dependencies**
```bash
    pip install -r requirements.txt
```
---

# Python Version
- Python 3.12.9
- pip 24.3.1

--- 

# 📌 Notes

- **YOLOv11** is used for object detection with images resized to **640×640**.

- Batch size, learning rate, and epochs can be adjusted in the `.yaml` config for your GPU capability.

- This system can process **live webcam feed**, stored videos, or image folders.
