import os
import sys
import subprocess


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
    choice = choose_device()
    install_torch(choice)
    install_project_requirements()
    print("\nSetup complete! You can now train:")
    if choice in {"g", "a"}:
        print("  python training.py --data Y3-v1/data.yaml --model yolov8n.pt --epochs 100 --device 0")
    else:
        print("  python training.py --data Y3-v1/data.yaml --model yolov8n.pt --epochs 100 --device cpu")


if __name__ == "__main__":
    main()


