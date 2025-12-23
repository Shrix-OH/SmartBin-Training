# This is the code I used for testing the serial communication and data transmission from the webcam.py script to the esp32
# Literally just toggles an led on the esp32 when space bar is pressed
# If your interested in getting something working or pseudocoding, can use this as an incredibly simple example of port communication
# Shrix-OH

import serial
import keyboard
import time

PORT = "COM3"  # Change to your ESP32 USB COM port
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # wait for ESP32 to initialize

print("Connected to ESP32 over USB")
print("Press SPACE to toggle LED. ESC to quit.")

while True:
    if keyboard.is_pressed("space"):
        ser.write(b"T")
        time.sleep(0.3)  # debounce

    if keyboard.is_pressed("esc"):
        break

ser.close()

