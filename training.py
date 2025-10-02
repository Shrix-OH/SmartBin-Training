import argparse
import zipfile
from pathlib import Path
import sys
import shutil
import yaml

try:
    from ultralytics import YOLO
except Exception as exc:
    print("Ultralytics is not installed. Please run: pip install -r requirements.txt")
    raise


def extract_dataset(zip_path: Path, extract_to: Path) -> Path:
    """Extract Roboflow dataset zip into extract_to, return root dir containing data.yaml."""
    extract_to.mkdir(parents=True, exist_ok=True)

    # Clean previous extraction folder with same name for a fresh state
    candidate_dir = extract_to / zip_path.stem
    if candidate_dir.exists():
        shutil.rmtree(candidate_dir)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)

    # Some Roboflow zips flatten, others create a folder. Search for data.yaml.
    return find_data_yaml_root(extract_to)


def find_data_yaml_root(search_dir: Path) -> Path:
    for path in search_dir.rglob('data.yaml'):
        return path.parent
    raise FileNotFoundError("Could not find data.yaml in extracted dataset")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv8n on a Roboflow dataset zip or data folder")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--zip", dest="zip_path", type=str,
                     help="Path to Roboflow dataset .zip")
    src.add_argument("--data", dest="data_path", type=str,
                     help="Path to folder containing data.yaml or to data.yaml itself")

    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--workers", type=int, default=2, help="Dataloader workers (Windows often needs small numbers)")
    parser.add_argument("--device", type=str, default=None, help="Device: 0 or cpu (None lets Ultralytics decide)")
    parser.add_argument("--project", type=str, default="runs/train", help="Project directory for outputs")
    parser.add_argument("--name", type=str, default="yolov8n-rf", help="Run name")
    parser.add_argument("--resume", action="store_true", help="Resume most recent run in project/name")
    parser.add_argument("--freeze", type=int, default=0, help="Number of layers to freeze")
    parser.add_argument("--lr0", type=float, default=0.01, help="Initial learning rate")
    parser.add_argument("--lrf", type=float, default=0.01, help="Final OneCycleLR learning rate fraction")
    parser.add_argument("--patience", type=int, default=50, help="Early stopping patience")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--cache", action="store_true", help="Cache images for faster training")
    return parser.parse_args()


def validate_data_yaml(data_root: Path) -> Path:
    data_yaml = data_root / 'data.yaml'
    if not data_yaml.exists():
        raise FileNotFoundError(f"Expected data.yaml at {data_yaml}")
    # Quick validation
    with open(data_yaml, 'r', encoding='utf-8') as f:
        data_cfg = yaml.safe_load(f) or {}
    for key in ["train", "val", "nc", "names"]:
        if key not in data_cfg:
            print(f"Warning: '{key}' not found in data.yaml. Ultralytics may still infer.")
    return data_yaml


def resolve_data_root_from_arg(data_arg: Path) -> Path:
    """Accept a folder or a direct data.yaml path and return the folder root containing data.yaml."""
    if data_arg.is_file():
        if data_arg.name != 'data.yaml':
            raise FileNotFoundError(f"If providing a file, it must be data.yaml, got: {data_arg}")
        return data_arg.parent
    if data_arg.is_dir():
        data_yaml = data_arg / 'data.yaml'
        if data_yaml.exists():
            return data_arg
    raise FileNotFoundError(f"Could not find data.yaml at or under {data_arg}")


def main() -> None:
    args = parse_args()

    datasets_dir = Path.cwd() / "datasets"

    if args.zip_path:
        zip_path = Path(args.zip_path).expanduser().resolve()
        if not zip_path.exists():
            print(f"Zip not found: {zip_path}")
            sys.exit(1)
        data_root = extract_dataset(zip_path, datasets_dir)
    else:
        data_arg = Path(args.data_path).expanduser().resolve()
        data_root = resolve_data_root_from_arg(data_arg)

    data_yaml = validate_data_yaml(data_root)

    model = YOLO("yolov8n.pt")

    train_kwargs = {
        "data": str(data_yaml),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "project": args.project,
        "name": args.name,
        "resume": args.resume,
        "freeze": args.freeze,
        "lr0": args.lr0,
        "lrf": args.lrf,
        "patience": args.patience,
        "seed": args.seed,
        "cache": args.cache,
    }
    if args.device is not None:
        train_kwargs["device"] = args.device

    results = model.train(**train_kwargs)
    print("Training complete. Results saved to:", Path(args.project) / args.name)


if __name__ == "__main__":
    main()
