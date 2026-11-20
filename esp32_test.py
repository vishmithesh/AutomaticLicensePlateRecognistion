import serial
import time

esp32 = serial.Serial("COM3", 115200, timeout=2)

time.sleep(2)

print("ESP32 connected")

esp32.write(b"TRIGGER\n")
esp32.flush()

print("TRIGGER command sent")

time.sleep(7)

while esp32.in_waiting:
    print(esp32.readline().decode(errors="replace").strip())

esp32.close()