I made this for training ml models to detect classes of rubbish in places like college campuses etc.
Has classes like plastic bottles, cans, paper, organics etc.
Free for anyone to use.

## Quick Start

### 1. Setup
```bash
python setup.py
```
Choose `g` for GPU or `c` for CPU when prompted.

### 2. Train Model
```bash
# GPU training
python training.py --data Y3-v3 --epochs 100 --device 0

# CPU training  
python training.py --data Y3-v3 --epochs 100 --device cpu
```

### 3. Run on Webcam
```bash
# GPU inference
python webcam.py --weights runs/train/yolov8n-rf/weights/best.pt --device 0

# CPU inference
python webcam.py --weights runs/train/yolov8n-rf/weights/best.pt --device cpu
```

That's it! Press `q` or `ESC` to quit the webcam.

## YOLOv8 Training and Webcam Inference

This project provides two scripts:

- `training.py`: Train a YOLOv8 model on a Roboflow-style dataset (zip or extracted folder with `data.yaml`).
- `webcam.py`: Run real-time inference from a webcam using trained weights.

### Folder Structure

- `Y3-v1`, `Y3-v2`, `Y3-v3`: Example datasets with `data.yaml`, `train/`, `valid/`, `test/`.
- `runs/train/...`: Ultralytics output directories (metrics, plots, and `weights/best.pt`).
- `yolov8n.pt`: The base YOLOv8n model used for training initialization.

### Requirements

Python 3.8–3.12 is recommended.

Install packages (quick path):

```bash
pip install -r requirements.txt
```

Note about PyTorch: Installing GPU-enabled PyTorch is platform- and CUDA/ROCm-specific. For a one-command setup, use the provided setup script which will ask CPU or GPU and install the appropriate PyTorch build first, then the rest of the requirements.

- PyTorch selector: `https://pytorch.org/get-started/locally/`

Examples:

- Windows with CUDA 12.x (PowerShell):
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

- Linux CUDA 12.x:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

- CPU-only (all platforms):
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Then install the rest:

```bash
pip install -r requirements.txt
### Quick Setup (interactive)

Use the interactive installer to choose GPU (CUDA) or CPU:

```bash
python setup.py
```

This will:
- Install PyTorch GPU wheels (CUDA 12.4) if you choose GPU, or CPU-only wheels otherwise
- Install project requirements from `requirements.txt`

```

### Training

`training.py` accepts either a Roboflow dataset zip (`--zip`) or a folder/file that contains `data.yaml` (`--data`). It will validate `data.yaml`, initialize YOLOv8n, and write results under `runs/train/<name>`.

Common flags:

- `--epochs` (default 100)
- `--imgsz` (default 640)
- `--batch` (default 16)
- `--workers` (default 2; on Windows keep small)
- `--device` (e.g. `0` for GPU 0, `cpu` for CPU; omit to let Ultralytics decide)
- `--project` (default `runs/train`)
- `--name` (run name; default `yolov8n-rf`)
- `--resume` (resume last run)
- `--freeze`, `--lr0`, `--lrf`, `--patience`, `--seed`, `--cache`

Run examples:

- Windows PowerShell (dataset already extracted at `Y3-v3`):
```powershell
python training.py --data Y3-v3 --epochs 100 --batch 16 --workers 2 --device 0 --name yolov8n-20e2
```

- Windows PowerShell (dataset zip at `C:\datasets\myset.zip`):
```powershell
python training.py --zip C:\datasets\myset.zip --epochs 50 --batch 8 --workers 2 --device cpu --name yolov8n-cpu
```

- Linux/macOS (dataset folder):
```bash
python3 training.py --data ./Y3-v3 --epochs 100 --batch 16 --workers 4 --device 0 --name yolov8n-20e2
```

- Linux/macOS (dataset zip):
```bash
python3 training.py --zip ~/datasets/myset.zip --epochs 50 --batch 8 --workers 4 --device 0 --name yolov8n-cu
```

Outputs will appear under `runs/train/<name>`. Best weights are at `runs/train/<name>/weights/best.pt`.

### Webcam Inference

Use `webcam.py` with your trained weights.

Common flags:

- `--weights` (required): path to `best.pt`
- `--device`: `0`, `0,1`, or `cpu` (optional)
- `--camera`: webcam index (default 0)
- `--imgsz`: inference image size (default 640)
- `--conf`: confidence threshold (default 0.25)
- `--iou`: NMS IoU threshold (default 0.45)
- `--show-fps`: overlay FPS counter

Run examples:

- Windows PowerShell:
```powershell
python webcam.py --weights .\runs\train\yolov8n-20e2\weights\best.pt --device 0 --camera 0 --show-fps
```

- Linux/macOS:
```bash
python3 webcam.py --weights ./runs/train/yolov8n-20e2/weights/best.pt --device 0 --camera 0 --show-fps
```

- CPU-only:
```bash
python3 webcam.py --weights ./runs/train/yolov8n-cpu/weights/best.pt --device cpu --camera 0
```

### Tips

- Keep `--workers` low on Windows to avoid DataLoader issues.
- Ensure `yolov8n.pt` is present in the project root for training initialization, or update the model path in `training.py`.
- If you hit CUDA/driver mismatches, confirm the Torch CUDA version matches your driver and rerun the Torch install step.



