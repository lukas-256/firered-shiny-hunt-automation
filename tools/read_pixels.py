import cv2

DEVICE_INDEX = 0  # change this

cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_AVFOUNDATION)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 60)

if not cap.isOpened():
    raise RuntimeError("Could not open capture card")

x, y = 100, 100  # pixel to inspect

while True:
    ok, frame = cap.read()
    if not ok:
        print("No frame")
        continue

    # OpenCV uses BGR, not RGB
    b, g, r = frame[y, x]
    print(f"Pixel at ({x},{y}): R={r} G={g} B={b}")

    # draw marker so you can see which pixel you're reading
    cv2.circle(frame, (x, y), 5, (0, 0, 255), 2)

    cv2.imshow("Capture", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
