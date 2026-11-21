# Automatic License Plate Recognition (ANPR) Smart Barrier System

An end-to-end **Computer Vision + IoT** access-control system that automatically detects Indian vehicle number plates using **Python (`OpenCV` + `EasyOCR`)**, logs vehicle timestamps in **SQLite**, visualizes traffic on a **Flask** dashboard, and triggers an **ESP32** traffic signal, 3-second alert buzzer, and servo barrier gate.

## Problem Statement

Conventional parking lots, campus gates, and gated facilities still rely on manual security checks and paper registers to track vehicles:

* **Slow gate throughput:** Manually checking and writing down license plates causes queues at entry and exit points.
* **Human error & missing records:** Handwritten logs are prone to typos, illegible entries, and missing exit times, making vehicle audits difficult.
* **Disconnected hardware control:** Security guards must manually operate barriers and alert signals separately from record-keeping.

## Proposed Solution

This project combines **real-time license plate recognition** with **automated ESP32 hardware actuation** in a single pipeline:

1. **Continuous Camera Monitoring:** While a vehicle approaches the gate, the **Red LED (`GPIO 25`)** remains ON and the **Servo Barrier (`GPIO 18`)** stays closed (`0°`).
2. **Automated OCR & Validation:** `OpenCV` captures live video frames and `EasyOCR` extracts the license plate text, validating it against an Indian vehicle registration regex (`^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{1,4}$`) with a confidence threshold and cooldown timer to prevent duplicate triggers.
3. **Structured Logging & Web Analytics:** Verified plates are saved with date, time, OCR confidence, location, and snapshot image into **SQLite (`traffic.db`)** and displayed live on a **Flask dashboard** (`http://127.0.0.1:5000`), supporting **IN / OUT** vehicle movement tracking.
4. **Synchronized Hardware Actuation:** Upon verification, Python sends a serial trigger (`115200` baud) to the **ESP32**, which switches from **Red** to **Green (`GPIO 26`)**, sounds the **Buzzer (`GPIO 23`)** for **3 seconds**, and lifts the **Servo Barrier (`GPIO 18`)** to `90°` before automatically resetting to Red (`0°`).

## System Architecture

```text
[ Camera / Webcam ]
        │  Video Frames
        ▼
[ Python ANPR Engine (main.py) ] ──► OpenCV Preprocessing + EasyOCR + Regex Validation
        │
        ├──► [ SQLite Database (database.py) ] ──► [ Flask Live Dashboard (dashboard.py) ]
        │         (Plate, Date, Time, Confidence, Image)         (http://127.0.0.1:5000)
        │
        └──► [ USB Serial (115200 baud) ]
                      │
                      ▼
             [ ESP32 Microcontroller ]
             ├── GPIO 25 → Red LED (Waiting / Gate Closed)
             ├── GPIO 26 → Green LED (Verified / Gate Open)
             ├── GPIO 23 → Active Buzzer (3s Audio Alert)
             └── GPIO 18 → SG90 Servo Motor (0° Closed → 90° Open)
```

## Live Demo Videos & Digital Hardware (Wokwi)

### Wokwi ESP32 Circuit Diagram



* **Run in Wokwi:** Open a [new Wokwi ESP32 project]<img width="1916" height="930" alt="Screenshot 2026-11-20 213526" src="https://github.com/user-attachments/assets/d6586cbf-cd20-4431-9f0a-531285e9fcc6" />
 and load `hardware/sketch.ino`, `hardware/diagram.json`, and `hardware/libraries.txt`.

### Demo 1: Smart Barrier & Hardware Simulation

[* Uploading anpr_real_capture_run.mp4…](https://github.com/user-attachments/assets/d1afe507-0f4a-4b33-8403-4394c24ff1c9)

### Demo 2: Live OpenCV Plate Capture & Database Logging

[* Uploading anpr_smart_barrier_demo.mp4…](https://github.com/user-attachments/assets/10e20efa-e809-4f15-86e3-181752b8dfd7)

## Hardware Pinout (ESP32 DevKit)

| Component | ESP32 Pin | Function |
| :--- | :--- | :--- |
| **Red LED** (+ 220 Ω resistor) | `GPIO 25` | ON by default while gate is closed |
| **Green LED** (+ 220 Ω resistor) | `GPIO 26` | Turns ON when a plate is verified |
| **Buzzer** | `GPIO 23` | Sounds for 3 seconds upon plate capture |
| **Servo Motor (SG90 Barrier)** | `GPIO 18` (`V+` → `5V`, `GND` → `GND`) | Rotates `0°` (Closed) → `90°` (Open) |
| **Camera Capture Button** *(Wokwi)* | `GPIO 19` (to `GND`) | Manual capture trigger in Wokwi simulator |
| **USB Serial Interface** | `UART0` (`115200` baud) | Receives `TRIGGER` / `IN` / `OUT` from `main.py` |

## Project File Structure

| File / Folder | Responsibility |
| :--- | :--- |
| `main.py` | Core application: camera capture, EasyOCR plate extraction, regex validation, SQLite storage, Flask thread, and ESP32 serial trigger |
| `database.py` | SQLite schema creation (`vehicle_records`), record insertion, and query helpers for total/daily vehicle counts |
| `dashboard.py` | Flask web dashboard displaying live vehicle logs and captured plate records at `http://127.0.0.1:5000` |
| `esp32_traffic_signal.ino` | ESP32 firmware controlling Red/Green LEDs, buzzer timing, and barrier actuation over `115200` baud serial |
| `anpr.py` | Standalone OpenCV + EasyOCR plate detection test script (without ESP32 or database) |
| `camera_test.py` | Quick verification utility to test webcam connectivity |
| `esp32_test.py` / `test_esp32.py` | Standalone serial test scripts to send `TRIGGER` commands to the ESP32 on `COM3` |
| `db_storage.py` | Database storage helper module |
| `requirements.txt` | Python dependencies (`opencv-python`, `easyocr`, `pyserial`, `flask`) |
| `hardware/` | Wokwi digital hardware files (`sketch.ino`, `diagram.json`, `libraries.txt`, `wokwi.toml`) |
| `docs/` | Wokwi circuit diagram (`docs/hardware/`) and demo GIF/MP4 recordings (`docs/demos/`) |

## Installation & Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/vishmithesh/AutomaticLicensePlateRecognistion.git
cd AutomaticLicensePlateRecognistion
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Flash ESP32 (or Simulate in Wokwi)
* Upload `esp32_traffic_signal.ino` (or `hardware/sketch.ino` for servo + buzzer support) to your ESP32 via Arduino IDE at `115200` baud and confirm your COM port (`COM3` by default in `main.py`).
* To simulate without physical hardware, load the `hardware/` files in [Wokwi](https://wokwi.com/esp32) or connect via [Wokwi for VS Code](https://docs.wokwi.com/vscode/getting-started) (`rfc2217://localhost:4000`).

### 4. Run the Application
```bash
python main.py
```
Open **`http://127.0.0.1:5000`** in your browser to view the live monitoring dashboard. Press **`Q`** in the OpenCV window to exit.

## Tech Stack

* **Computer Vision & OCR:** Python, OpenCV, EasyOCR
* **Backend & Storage:** Flask, SQLite3
* **Embedded & IoT:** ESP32 (Arduino C++), PySerial (`115200` baud), Wokwi Simulator

## Future Enhancements

* Automatic **IN / OUT** entry-exit duration calculation per vehicle in `database.py` and `dashboard.py`
* **ESP32-CAM** Wi-Fi MJPEG stream integration for wireless gate deployment
* Authorized/blacklisted vehicle alert rules on the Flask dashboard
