import os
import sys
import subprocess


def is_in_virtualenv() -> bool:
    """Detect if we're running inside a virtual environment."""
    # Check for venv (Python 3.3+)
    if getattr(sys, "base_prefix", sys.prefix) != sys.prefix:
        return True
    # Check for virtualenv (older style)
    if hasattr(sys, "real_prefix"):
        return True
    # Check environment variable
    if os.environ.get("VIRTUAL_ENV"):
        return True
    # Additional check: see if we're running from a venv python executable
    if "/.venv/" in sys.executable or "\\.venv\\" in sys.executable:
        return True
    # Check if we're in a conda environment
    if os.environ.get("CONDA_DEFAULT_ENV"):
        return True
    return False


def get_project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_venv_python_path(venv_root: str) -> str:
    if os.name == "nt":
        return os.path.join(venv_root, "Scripts", "python.exe")
    return os.path.join(venv_root, "bin", "python")


def ensure_virtualenv() -> None:
    """Create .venv if absent and re-execute this script inside it."""
    if is_in_virtualenv():
        print("Already running inside virtual environment.")
        return

    project_root = get_project_root()
    venv_dir = os.path.join(project_root, ".venv")
    venv_python = get_venv_python_path(venv_dir)

    if not os.path.exists(venv_python):
        print("Creating virtual environment at .venv ...")
        try:
            code = subprocess.call([sys.executable, "-m", "venv", venv_dir])
            if code != 0:
                print("ERROR: Failed to create virtual environment.")
                print("Please ensure you have Python 3.3+ and the venv module is available.")
                print("You can try creating it manually with:")
                print(f"  python -m venv {venv_dir}")
                sys.exit(code)
            print("Virtual environment created successfully.")
        except FileNotFoundError:
            print("ERROR: Python executable not found. Please ensure Python is in your PATH.")
            sys.exit(1)
    else:
        print("Found existing .venv directory.")

    # Verify the venv python exists
    if not os.path.exists(venv_python):
        print(f"ERROR: Virtual environment Python not found at: {venv_python}")
        print("The .venv directory may be corrupted. Please delete it and run setup again.")
        sys.exit(1)

    # ALWAYS re-exec inside the venv when not already in one
    print("Re-running setup inside .venv ...")
    try:
        code = subprocess.call([venv_python, os.path.abspath(__file__)] + sys.argv[1:])
        sys.exit(code)
    except FileNotFoundError:
        print(f"ERROR: Failed to execute Python in virtual environment: {venv_python}")
        sys.exit(1)


def run(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("Error: command not found:", cmd[0])
        return 1


def pip_install(args: list[str]) -> int:
    python = sys.executable
    return run([python, "-m", "pip", "install", "--upgrade", "pip"]) or run([python, "-m", "pip", "install"] + args)


def choose_device() -> str:
    print("Select install target for PyTorch:")
    print("  [g] GPU (CUDA/NVIDIA)")
    print("  [a] GPU (ROCm/AMD, Linux)")
    print("  [r] CPU (ROCm runtime, AMD, Linux)")
    print("  [c] CPU only")
    choice = input("Enter g, a, r or c: ").strip().lower()
    if choice not in {"g", "a", "r", "c"}:
        print("Invalid choice. Please run again and enter 'g', 'a', 'r' or 'c'.")
        sys.exit(1)
    return choice


def install_torch(choice: str) -> None:
    if choice == "g":
        # Default to CUDA 12.4 wheels which work with recent NVIDIA drivers.
        # Users can change the index URL if they need a different CUDA version.
        index_url = "https://download.pytorch.org/whl/cu124"
        print("Installing PyTorch (GPU, CUDA 12.4 wheels)...")
        code = pip_install(["torch", "torchvision", "--index-url", index_url])
        if code != 0:
            print("PyTorch (GPU) install failed. You may need a different CUDA wheel. See https://pytorch.org/get-started/locally/")
            sys.exit(code)
    elif choice == "a":
        # ROCm GPU wheels (Linux only). Adjust if your system uses a different ROCm version.
        index_url = "https://download.pytorch.org/whl/rocm6.0"
        print("Installing PyTorch (GPU, ROCm 6.0 wheels for AMD, Linux only)...")
        code = pip_install(["torch", "torchvision", "--index-url", index_url])
        if code != 0:
            print("PyTorch (GPU/ROCm) install failed. See https://pytorch.org/get-started/locally/")
            sys.exit(code)
    elif choice == "r":
        # ROCm CPU runtime wheels: use CPU wheels but allow AMD users on Linux without CUDA.
        # Note: PyTorch does not ship a separate 'ROCm CPU' wheel; CPU wheel is used.
        index_url = "https://download.pytorch.org/whl/cpu"
        print("Installing PyTorch (CPU wheels for ROCm CPU path, Linux)...")
        code = pip_install(["torch", "torchvision", "--index-url", index_url])
        if code != 0:
            print("PyTorch (CPU) install failed. See https://pytorch.org/get-started/locally/")
            sys.exit(code)
    else:
        print("Installing PyTorch (CPU-only wheels)...")
        index_url = "https://download.pytorch.org/whl/cpu"
        code = pip_install(["torch", "torchvision", "--index-url", index_url])
        if code != 0:
            print("PyTorch (CPU) install failed. See https://pytorch.org/get-started/locally/")
            sys.exit(code)


def install_project_requirements() -> None:
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(req_file):
        print("requirements.txt not found next to setup.py")
        sys.exit(1)
    print("Installing project requirements from requirements.txt...")
    code = pip_install(["-r", req_file])
    if code != 0:
        print("Failed to install project requirements.")
        sys.exit(code)


def main() -> None:
    # Always bootstrap a local venv and run inside it
    ensure_virtualenv()
    
    # If we reach here, we're guaranteed to be inside the virtual environment
    print(f"Running setup inside virtual environment: {os.environ.get('VIRTUAL_ENV', 'detected')}")
    
    choice = choose_device()
    install_torch(choice)
    install_project_requirements()
    print("\nSetup complete! You can now train:")
    print("\nTo activate the virtual environment in future sessions:")
    if os.name == "nt":
        print("  # Windows PowerShell:")
        print("  ./.venv/Scripts/Activate.ps1")
        print("  # Windows Command Prompt:")
        print("  .venv\\Scripts\\activate.bat")
    else:
        print("  # Linux/macOS:")
        print("  source .venv/bin/activate")
    
    print("\nTraining commands:")
    if choice in {"g", "a"}:
        print("  python training.py --data Y3-v1/data.yaml --model yolov8n.pt --epochs 100 --device 0")
        print("  # Or on Linux: python3 training.py --data Y3-v1/data.yaml --model yolov8n.pt --epochs 100 --device 0")
    else:
        print("  python training.py --data Y3-v1/data.yaml --model yolov8n.pt --epochs 100 --device cpu")
        print("  # Or on Linux: python3 training.py --data Y3-v1/data.yaml --model yolov8n.pt --epochs 100 --device cpu")


if __name__ == "__main__":
    main()


