
import cv2
import easyocr
import serial
import re
import os
import time
import threading

from datetime import datetime

from database import create_table, insert_vehicle
from dashboard import start_dashboard


# ---------------- CONFIGURATION ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERIAL_PORT = "COM3"
BAUD_RATE = 115200

CAMERA_INDEX = 0

CONFIDENCE_THRESHOLD = 0.50
COOLDOWN_SECONDS = 12

CAPTURE_FOLDER = os.path.join(BASE_DIR, "captures")

LOCATION = "Coimbatore"

PLATE_PATTERN = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{1,4}$"


# ---------------- STATUS VARIABLES ----------------

status_text = "SYSTEM READY - WAITING FOR VEHICLE"

detected_plate = ""

status_until = 0

status_color = (0, 255, 255)


# ---------------- INITIALIZATION ----------------

os.makedirs(CAPTURE_FOLDER, exist_ok=True)

create_table()

print("Loading EasyOCR...")

reader = easyocr.Reader(["en"], gpu=False)


# ---------------- ESP32 CONNECTION ----------------

print("Connecting to ESP32...")

try:

    esp32 = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=1
    )

    time.sleep(2)

    print("ESP32 connected successfully.")

except serial.SerialException as error:

    print("ESP32 connection failed:", error)

    print("Check COM port and close Arduino Serial Monitor.")

    raise SystemExit


# ---------------- DASHBOARD ----------------

dashboard_thread = threading.Thread(
    target=start_dashboard,
    daemon=True
)

dashboard_thread.start()


# ---------------- CAMERA ----------------

camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():

    print("Camera not detected.")

    esp32.close()

    raise SystemExit


print("ALPR SYSTEM STARTED")

print("Dashboard: http://127.0.0.1:5000")

print("Press Q to exit.")


last_detection_time = 0


# ---------------- MAIN PROCESSING ----------------

try:

    while True:

        ret, frame = camera.read()

        if not ret:

            print("Unable to capture image.")

            break


        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        results = reader.readtext(gray)


        for detection in results:

            bbox, detected_text, confidence = detection


            # Normalize detected plate text

            plate = re.sub(
                r"[^A-Z0-9]",
                "",
                detected_text.upper()
            )


            # Validate plate and OCR confidence

            if (

                re.fullmatch(PLATE_PATTERN, plate)

                and confidence >= CONFIDENCE_THRESHOLD

            ):

                current_time = time.time()


                # Apply cooldown

                if current_time - last_detection_time < COOLDOWN_SECONDS:

                    continue


                # ---------------- DATE AND TIME ----------------

                now = datetime.now()

                date_string = now.strftime("%Y-%m-%d")

                time_string = now.strftime("%H:%M:%S")

                filename_time = now.strftime("%Y%m%d_%H%M%S")


                # ---------------- CONFIDENCE CONVERSION ----------------

                confidence_percentage = float(confidence) * 100


                # ---------------- SAVE IMAGE ----------------

                filename = f"{plate}_{filename_time}.jpg"

                image_path = os.path.join(
                    CAPTURE_FOLDER,
                    filename
                )


                saved = cv2.imwrite(
                    image_path,
                    frame
                )


                if not saved:

                    print("Image could not be saved.")

                    status_text = "IMAGE SAVE FAILED"

                    status_color = (0, 0, 255)

                    status_until = time.time() + 5

                    continue


                # ---------------- SAVE DATABASE RECORD ----------------

                try:

                    record_id = insert_vehicle(

                        plate,

                        date_string,

                        time_string,

                        confidence_percentage,

                        filename,

                        image_path,

                        location=LOCATION

                    )


                except Exception as error:

                    print("Database error:", error)

                    if os.path.exists(image_path):

                        os.remove(image_path)


                    status_text = "DATABASE SAVE FAILED"

                    status_color = (0, 0, 255)

                    status_until = time.time() + 5

                    continue


                # ---------------- SUCCESS STATUS ----------------

                print("\nVEHICLE DETECTED")

                print("Plate:", plate)

                print("Date:", date_string)

                print("Time:", time_string)

                print(
                    "Confidence:",
                    round(confidence_percentage, 2),
                    "%"
                )

                print("Database ID:", record_id)

                print("Image saved:", image_path)


                status_text = "VEHICLE DETECTED - STORED"

                status_color = (0, 255, 0)

                detected_plate = plate

                status_until = time.time() + 5


                # ---------------- SEND ESP32 COMMAND ----------------

                try:

                    esp32.write(b"TRIGGER\n")

                    esp32.flush()

                    print("Traffic signal activated.")

                    status_text = "VEHICLE STORED - SIGNAL ACTIVATED"

                    status_until = time.time() + 5


                except serial.SerialException as error:

                    print("ESP32 communication error:", error)

                    status_text = "STORED - ESP32 ERROR"

                    status_color = (0, 165, 255)

                    status_until = time.time() + 5


                last_detection_time = current_time


                # ---------------- DRAW PLATE BOUNDARY ----------------

                points = [

                    (int(x), int(y))

                    for x, y in bbox

                ]


                for i in range(4):

                    cv2.line(

                        frame,

                        points[i],

                        points[(i + 1) % 4],

                        (0, 255, 0),

                        2

                    )


                cv2.putText(

                    frame,

                    plate,

                    points[0],

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.8,

                    (0, 255, 0),

                    2

                )


                break


        # ---------------- CAMERA STATUS DISPLAY ----------------

        height, width = frame.shape[:2]


        cv2.rectangle(

            frame,

            (0, 0),

            (width, 115),

            (30, 30, 30),

            -1

        )


        cv2.putText(

            frame,

            "ALPR VEHICLE MONITORING SYSTEM",

            (15, 30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2

        )


        if time.time() < status_until:

            cv2.putText(

                frame,

                status_text,

                (15, 65),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                status_color,

                2

            )


            cv2.putText(

                frame,

                "PLATE: " + detected_plate,

                (15, 98),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2

            )


        else:

            cv2.putText(

                frame,

                "STATUS: WAITING FOR VEHICLE",

                (15, 65),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 255, 255),

                2

            )


            cv2.putText(

                frame,

                "LAST PLATE: " + (

                    detected_plate if detected_plate else "NONE"

                ),

                (15, 98),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2

            )


        cv2.imshow(

            "ALPR Vehicle Monitoring System",

            frame

        )


        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


finally:

    camera.release()

    cv2.destroyAllWindows()


    if esp32.is_open:

        esp32.close()


    print("ALPR system stopped.")
