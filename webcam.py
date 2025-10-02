import argparse
from pathlib import Path
import sys
import time

import cv2
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Webcam inference with YOLOv8")
    parser.add_argument("--weights", type=str, required=True,
                        help="Path to trained weights (e.g., runs/train/exp/weights/best.pt)")
    parser.add_argument("--device", type=str, default=None, help="Device: 0, 0,1 or cpu")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (0 is default laptop camera)")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--show-fps", action="store_true", help="Overlay FPS on the frame")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    weights_path = Path(args.weights).expanduser().resolve()
    if not weights_path.exists():
        print(f"Weights not found: {weights_path}")
        sys.exit(1)

    model = YOLO(str(weights_path))
    if args.device is not None:
        model.to(args.device)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera index {args.camera}")
        sys.exit(1)

    window_name = "YOLOv8 Webcam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    prev_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            break

        results = model.predict(source=frame, imgsz=args.imgsz, conf=args.conf, iou=args.iou, verbose=False)
        plotted = results[0].plot()

        if args.show_fps:
            cur_time = time.time()
            fps = 1.0 / max(cur_time - prev_time, 1e-6)
            prev_time = cur_time
            cv2.putText(plotted, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        cv2.imshow(window_name, plotted)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
