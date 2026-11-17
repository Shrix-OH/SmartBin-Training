# Code that uses a webcam to perform real-time object detection with YOLO
# Shrix-OH

# Required imports
import argparse
from pathlib import Path
import sys

# Computer vision and YOLOv8 imports
import cv2
from ultralytics import YOLO

def parse_args() -> argparse.Namespace:

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Webcam inference with YOLO")

    # Inference parameters
    parser.add_argument("--weights", type=str, required=True, help="Path to trained weights (e.g., runs/train/exp/weights/best.pt)")
    parser.add_argument("--device", type=str, default=None, help="Device: 0, 0,1 or cpu")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (0 is default laptop camera, 1 for external USB camera)")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument("--conf", type=float, default=0.15, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")

    return parser.parse_args()

def main() -> None:
    # Parse command-line arguments
    args = parse_args()

    # Validate weights path
    weights_path = Path(args.weights).expanduser().resolve()
    if not weights_path.exists():
        print(f"Weights not found: {weights_path}")
        sys.exit(1)

    # Load the model
    model = YOLO(str(weights_path))
    if args.device is not None:
        model.to(args.device)

    # Open webcam
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera index {args.camera}")
        sys.exit(1)

    # Create display window
    window_name = "YOLOv8 Webcam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Main inference loop
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            break

        # Perform inference
        results = model.predict(source=frame, imgsz=args.imgsz, conf=args.conf, iou=args.iou, verbose=False)

        # Get plotted frame
        plotted = results[0].plot()

        cv2.imshow(window_name, plotted)

        # Exit on ESC or 'q' key
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

# Run the main function
if __name__ == "__main__":
    main()
