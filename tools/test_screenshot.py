import cv2
import numpy as np
import time

REFERENCE_PATH = "switch_frame_game_freak.png"
DEVICE_INDEX = 0          # change to 1, 2, ... if needed
PIXEL_TOLERANCE = 1
SIMILARITY_THRESHOLD = 0.99
CHECK_INTERVAL_SECONDS = 0.5

reference = cv2.imread(REFERENCE_PATH)

if reference is None:
    raise RuntimeError(f"Could not load reference image: {REFERENCE_PATH}")

cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    raise RuntimeError("Could not open capture device")

try:
    while True:
        ok, frame = cap.read()

        if not ok:
            print("match negative ----")
            time.sleep(CHECK_INTERVAL_SECONDS)
            continue

        if frame.shape != reference.shape:
            frame = cv2.resize(frame, (reference.shape[1], reference.shape[0]))

        diff = cv2.absdiff(reference, frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        same_pixels = np.sum(gray_diff < PIXEL_TOLERANCE)
        total_pixels = gray_diff.size
        similarity = same_pixels / total_pixels

        if similarity >= SIMILARITY_THRESHOLD:
            print("match positive ++++")
        else:
            print("match negative ----")

        time.sleep(CHECK_INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("stopped by user")

finally:
    cap.release()
