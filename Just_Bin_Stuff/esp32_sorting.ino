// This is the code I used for testing the lcd display, Bluetooth communication and data transmission from the webcam.py script to the esp32
// Just prints the detected class name to the lcd display
// Not for final use, just sharing for others to use as a reference (Confirmed working)
// Shrix-OH




// ESP32 Waste Sorting Display
// Receives detected class names from webcam.py over Bluetooth and displays on LCD

// Use hd44780 library (ESP32 compatible)
// Install via Arduino IDE: Sketch > Include Library > Manage Libraries > search "hd44780"
#include <Wire.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>
#include "BluetoothSerial.h"

// Bluetooth Serial
BluetoothSerial SerialBT;

// LCD setup - auto-detects I2C address
hd44780_I2Cexp lcd;

// LCD geometry
const int LCD_COLS = 16;
const int LCD_ROWS = 2;

// Buffer for incoming data
String inputBuffer = "";
String currentClass = "";

void setup() {
  // Initialize USB serial for debugging
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  // Initialize Bluetooth
  if (!SerialBT.begin("ESP32_Sorter")) {
    Serial.println("Bluetooth init failed!");
    while (1);
  }
  Serial.println("Bluetooth started. Pair with 'ESP32_Sorter'");
  
  // Initialize I2C on ESP32 pins
  Wire.begin(21, 22);  // SDA=21, SCL=22 for ESP32
  
  // Initialize LCD
  int status = lcd.begin(LCD_COLS, LCD_ROWS);
  if (status) {
    // If LCD init fails, blink the built-in LED
    Serial.print("LCD init failed, status: ");
    Serial.println(status);
    pinMode(2, OUTPUT);
    while (1) {
      digitalWrite(2, HIGH);
      delay(200);
      digitalWrite(2, LOW);
      delay(200);
    }
  }
  
  lcd.backlight();
  
  // Display startup message
  lcd.setCursor(0, 0);
  lcd.print("Waste Sorter");
  lcd.setCursor(0, 1);
  lcd.print("BT: ESP32_Sorter");
  
  Serial.println("ESP32 Waste Sorter Ready (Bluetooth)");
}

void loop() {
  // Check for incoming Bluetooth data
  while (SerialBT.available()) {
    char c = SerialBT.read();
    
    if (c == '\n') {
      // End of message, process it
      inputBuffer.trim();
      
      if (inputBuffer.length() > 0 && inputBuffer != currentClass) {
        currentClass = inputBuffer;
        updateDisplay(currentClass);
        Serial.print("Displaying: ");
        Serial.println(currentClass);
        // Echo back over Bluetooth for confirmation
        SerialBT.println("OK: " + currentClass);
      }
      
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }
}

void updateDisplay(String className) {
  lcd.clear();
  
  if (className == "NONE") {
    lcd.setCursor(0, 0);
    lcd.print("Scanning...");
    lcd.setCursor(0, 1);
    lcd.print("No object");
  } else {
    lcd.setCursor(0, 0);
    lcd.print("Detected:");
    lcd.setCursor(0, 1);
    // Truncate if longer than 16 chars (LCD width)
    if (className.length() > 16) {
      lcd.print(className.substring(0, 16));
    } else {
      lcd.print(className);
    }
  }
}
