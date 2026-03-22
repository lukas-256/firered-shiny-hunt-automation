import cv2

DEVICE_INDEX = int(input("Number: "))  # try 0, then 1

cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    raise RuntimeError(f"Could not open device {DEVICE_INDEX}")

while True:
    ok, frame = cap.read()
    if not ok:
        print("No frame")
        continue

    cv2.imshow(f"Device {DEVICE_INDEX}", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
