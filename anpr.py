
import cv2
import easyocr
import re

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Open laptop webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not detected")
    exit()

print("ANPR System Started")
print("Press Q to exit")

while True:

    ret, frame = camera.read()

    if not ret:
        print("Unable to capture frame")
        break

    # Convert image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform OCR
    results = reader.readtext(gray)

    for detection in results:

        bbox, text, confidence = detection

        # Clean recognized text
        plate = re.sub(r'[^A-Z0-9]', '', text.upper())

        # Basic Indian registration number pattern
        pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$'

        if re.match(pattern, plate):

            print("NUMBER PLATE:", plate)
            print("CONFIDENCE:", round(confidence, 2))

            # Draw bounding box
            points = [(int(x), int(y)) for x, y in bbox]

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

    cv2.imshow("ANPR System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()