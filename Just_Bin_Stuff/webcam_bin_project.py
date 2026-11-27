# Code that uses a webcam to perform real-time object detection with YOLOv8 / Soon to be V12
# Sends detected class names to an ESP32 over Bluetooth for display on an LCD
# Shrix-OH

# Required imports
import argparse
from pathlib import Path
import sys
import time
import serial

# Computer vision and YOLOv8 imports
import cv2
from ultralytics import YOLO

# ESP32 Bluetooth Connection Settings
# After pairing with "ESP32_Sorter" in Windows Bluetooth settings,
# find the outgoing COM port in Device Manager > Ports (COM & LPT)
# It will show as "Standard Serial over Bluetooth link (COM#)"
ESP32_PORT = "COM7"  # Change to your Bluetooth COM port (check Device Manager after pairing)
ESP32_BAUD = 115200


def parse_args() -> argparse.Namespace:

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Webcam inference with YOLOv8 + ESP32 control")

    # Inference parameters
    parser.add_argument("--weights", type=str, required=True, help="Path to trained weights (e.g., runs/train/exp/weights/best.pt)")
    parser.add_argument("--device", type=str, default=None, help="Device: 0, 0,1 or cpu")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (0 is default laptop camera, 1 for external USB camera)")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="NMS IoU threshold")

    parser.add_argument("--no-esp32", action="store_true", help="Disable ESP32 communication")
    
    return parser.parse_args()

# Function to get detected class name
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

    # Connect to ESP32 via Bluetooth (uses virtual COM port)
    esp32 = None
    if not args.no_esp32:
        try:
            print(f"Connecting to ESP32 via Bluetooth on {ESP32_PORT}...")
            esp32 = serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=1)
            time.sleep(2)  # Wait for Bluetooth connection to stabilize
            print(f"Connected to ESP32 via Bluetooth on {ESP32_PORT}")
        except serial.SerialException as e:
            print(f"Failed to connect to ESP32 via Bluetooth: {e}")
            print("Make sure you have paired with 'ESP32_Sorter' in Windows Bluetooth settings.")
            print("Running without ESP32 connection.")

    # Open webcam
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera index {args.camera}")
        sys.exit(1)

    # Create display window
    window_name = "YOLOv8 Webcam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Last sent class name to avoid sending the same class name multiple times
    last_sent_class = None
    
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

        # Get detected class name and send to ESP32
        class_name = get_detected_class_name(results, model)
        if class_name is not None and class_name != last_sent_class:
            # Send class name to ESP32 for LCD display
            if esp32 and esp32.is_open:
                esp32.write(f"{class_name}\n".encode('utf-8'))
                #print(f"Sent '{class_name}' to ESP32") Debugging line
            last_sent_class = class_name
        elif class_name is None and last_sent_class is not None:
            # Send NONE when nothing detected
            if esp32 and esp32.is_open:
                esp32.write(b"NONE\n")
            last_sent_class = None
        
        # Display ESP32 status
        esp32_status = "ESP32: Bluetooth Connected" if esp32 and esp32.is_open else "ESP32: Disconnected"
        cv2.putText(plotted, esp32_status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow(window_name, plotted)

        # Exit on ESC or 'q' key
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    # Cleanup
    if esp32 and esp32.is_open:
        esp32.close()
    cap.release()
    cv2.destroyAllWindows()

# Run the main function
if __name__ == "__main__":
    main()
