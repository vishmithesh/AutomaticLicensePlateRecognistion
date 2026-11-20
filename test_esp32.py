import serial
import time

PORT = "COM3"
BAUD_RATE = 115200

try:
    esp32 = serial.Serial(PORT, BAUD_RATE, timeout=2)

    time.sleep(2)

    print("ESP32 connected successfully")

    esp32.write(b"TRIGGER\n")
    esp32.flush()

    print("TRIGGER command sent")

    start = time.time()

    while time.time() - start < 8:
        if esp32.in_waiting:
            message = esp32.readline().decode(
                "utf-8",
                errors="replace"
            ).strip()

            if message:
                print("ESP32:", message)

    esp32.close()

except serial.SerialException as error:
    print("Serial communication error:", error)