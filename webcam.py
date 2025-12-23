# Code that uses a webcam to perform real-time object detection with YOLOv8 / Soon to be V12
# Sends detected class names to an ESP32 over serial for display on an LCD
# Shrix-OH

import argparse
from pathlib import Path
import sys
import time
import serial

import cv2
from ultralytics import YOLO

# ESP32 Serial Connection Settings (same as testing.py)
ESP32_PORT = "COM3"  # Change to your ESP32 USB COM port
ESP32_BAUD = 115200


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Webcam inference with YOLOv8 + ESP32 control")
    parser.add_argument("--weights", type=str, required=True,
                        help="Path to trained weights (e.g., runs/train/exp/weights/best.pt)")
    parser.add_argument("--device", type=str, default=None, help="Device: 0, 0,1 or cpu")

    # Change below to 1 for usb camera
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (0 is default laptop camera)")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--show-fps", action="store_true", help="Overlay FPS on the frame")
    parser.add_argument("--no-esp32", action="store_true", help="Disable ESP32 communication")
    
    return parser.parse_args()


def get_detected_class_name(results, model) -> str | None:
    """Extract the class name of the first detected object."""
    if len(results) == 0 or len(results[0].boxes) == 0:
        return None
    
    # Get the class ID of the first detected object
    class_id = int(results[0].boxes.cls[0].item())
    # Get the class name from the model
    class_name = model.names[class_id]
    return class_name


def main() -> None:
    args = parse_args()

    weights_path = Path(args.weights).expanduser().resolve()
    if not weights_path.exists():
        print(f"Weights not found: {weights_path}")
        sys.exit(1)

    model = YOLO(str(weights_path))
    if args.device is not None:
        model.to(args.device)

    # Connect to ESP32 using simple method (same as testing.py)
    esp32 = None
    if not args.no_esp32:
        try:
            esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=1)
            time.sleep(2)  # Wait for ESP32 to initialize
            print(f"Connected to ESP32 on {ESP32_PORT}")
        except serial.SerialException as e:
            print(f"Failed to connect to ESP32: {e}")
            print("Running without ESP32 connection.")

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera index {args.camera}")
        sys.exit(1)

    window_name = "YOLOv8 Webcam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    prev_time = time.time()
    last_sent_class = None  # Track last sent class to avoid spamming
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            break

        results = model.predict(source=frame, imgsz=args.imgsz, conf=args.conf, iou=args.iou, verbose=False)
        plotted = results[0].plot()

        # Get detected class name and send to ESP32
        class_name = get_detected_class_name(results, model)
        if class_name is not None and class_name != last_sent_class:
            # Send class name to ESP32 for LCD display
            if esp32 and esp32.is_open:
                esp32.write(f"{class_name}\n".encode('utf-8'))
                print(f"Sent '{class_name}' to ESP32")
            last_sent_class = class_name
        elif class_name is None and last_sent_class is not None:
            # Send clear signal when nothing detected
            if esp32 and esp32.is_open:
                esp32.write(b"NONE\n")
            last_sent_class = None

        if args.show_fps:
            cur_time = time.time()
            fps = 1.0 / max(cur_time - prev_time, 1e-6)
            prev_time = cur_time
            cv2.putText(plotted, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Display ESP32 status
        esp32_status = "ESP32: Connected" if esp32 and esp32.is_open else "ESP32: Disconnected"
        cv2.putText(plotted, esp32_status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow(window_name, plotted)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    # Cleanup
    if esp32 and esp32.is_open:
        esp32.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
