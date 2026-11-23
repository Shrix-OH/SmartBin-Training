I made this for training ml models to detect classes of rubbish in places like college campuses etc.
Has classes like plastic bottles, cans, paper, organics etc.

Use python 3.8 - 3.12 for venv creation, otherwise issues will likely arise.
I used 3.12 and it works without any identifiable issues.

## Quick Start

### 1. Setup (Automatic Virtual Environment)

FIRST THING TO DO !!!!!!!
cd into the correct directory

```bash
# Make sure you're in the directory containing all the files (e.g. Y3-v1, Y3-v2, Y3-v3, runs/train etc) 
cd SmartBin-Training
```

The setup script **automatically creates and uses a virtual environment** - you don't need to create one manually!

```bash
# Windows:
python setup.py

# Linux/macOS (use python3 if python points to Python 2.x):
python setup.py
# or
python3 setup.py
```

**What happens:**
1. The script detects if you're already in a virtual environment
2. If not, it creates a `.venv` folder in the project directory
3. It automatically re-runs itself inside the virtual environment
4. All packages are installed safely in the isolated environment

Choose your hardware when prompted:
- `g` = NVIDIA GPU (CUDA)
- `a` = AMD GPU (ROCm, Linux)
- `r` = AMD ROCm CPU runtime (Linux)
- `c` = CPU only (all platforms)

**For future sessions**, activate the virtual environment:
- Windows (PowerShell): `./.venv/Scripts/Activate.ps1`
- Windows (Command Prompt): `.venv\Scripts\activate.bat`
- Linux/macOS (bash/zsh): `source .venv/bin/activate`

**Important:** The setup script ensures everything is installed in a virtual environment regardless of your choice - this protects your system Python installation.

IMPORTANT
Before running training or webcam, you must activate the env

```bash
# Windows etc
./.venv/Scripts/Activate.ps1

# Linux 
source .venv/bin/activate
```

### 2. Train Model
```bash

# There are 3 different datasets
# V1 has 800 images, V2 has like 4,000 and V3 has almost 15,000
# When choosing what dataset to use in training, use Y3-v1, Y3-v2 or Y3-v3
# Commands below use v3 but for simple use you could use v2 instead 


# Using GPU
python training.py --data Y3-v3 --epochs 100 --device 0
# Or on Linux: python3 training.py --data Y3-v3 --epochs 100 --device 0
# Train with as many epochs as you want 100 could take a while

# Using CPU  
python training.py --data Y3-v3 --epochs 100 --device cpu
# Or on Linux: python3 training.py --data Y3-v3 --epochs 100 --device cpu
# Train with as many epochs as you want 100 could take a while
```

### 3. Run on Webcam
```bash
# Using GPU 
python webcam.py --weights runs/train/yolov8n-20e2/weights/best.pt --device 0
# Or on Linux: python3 webcam.py --weights runs/train/yolov8n-rf/weights/best.pt --device 0

# Using CPU 
python webcam.py --weights runs/train/yolov8n-20e2/weights/best.pt --device cpu
# Or on Linux: python3 webcam.py --weights runs/train/yolov8n-rf/weights/best.pt --device cpu
```

That's it! Press `q` or `ESC` to quit the webcam.
Or if that doesnt work click ctrl c in the terminal running the webcam

``` ############################################################## ```
``` YOU SHOULDNT HAVE TO DO ANYTHING PAST HERE IF EVERYTHING WORKS ```
``` ############################################################## ```



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

- Linux with ROCm 6.x (AMD GPUs):
```bash
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
```

- Linux with ROCm CPU path (no GPU compute):
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

- CPU-only (all platforms):
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Then install the rest:

```bash
pip install -r requirements.txt
```

### Quick Setup (Interactive - Recommended)

**The setup script automatically handles virtual environment creation and package installation:**

```bash
# Windows:
python setup.py

# Linux/macOS:
python setup.py
# or if python points to Python 2.x:
python3 setup.py
```

**This automatically:**
1. **Creates a `.venv` virtual environment** (if not already in one)
2. **Re-runs itself inside the virtual environment**
3. Installs PyTorch wheels for your chosen backend:
   - CUDA (cu124) for `g`
   - ROCm 6.0 for `a` (Linux)
   - CPU wheels for `r` (ROCm CPU path, Linux) and `c`
4. Installs all project requirements from `requirements.txt`

**No manual virtual environment setup required!** The script ensures everything is isolated from your system Python.

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
- On ROCm (Linux), verify install with:
  ```bash
  python -c "import torch; print(torch.cuda.is_available(), getattr(torch.version, 'hip', None))"
  ```
  For ROCm GPU (`a`), `cuda.is_available()` should be True and `hip` should show a version. For ROCm CPU (`r`), expect CPU usage.

### Virtual Environment Troubleshooting

**If the setup script fails to create a virtual environment:**
1. Ensure Python 3.3+ is installed: `python --version`
2. Verify the `venv` module is available: `python -m venv --help`
3. Manually create the virtual environment:
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate it
   # Windows PowerShell:
   ./.venv/Scripts/Activate.ps1
   # Windows Command Prompt:
   .venv\Scripts\activate.bat
   # Linux/macOS:
   source .venv/bin/activate
   
   # Run setup again
   python setup.py
   ```

**If packages are still installing globally:**
- The setup script should prevent this, but if it happens, delete `.venv` and run `python setup.py` again
- Verify you're in the virtual environment by checking if the prompt shows `(.venv)` or similar



