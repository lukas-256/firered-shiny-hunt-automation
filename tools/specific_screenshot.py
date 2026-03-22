import cv2

DEVICE_INDEX = 0
cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_AVFOUNDATION)

ok, frame = cap.read()
cap.release()

if not ok:
    raise RuntimeError("Could not grab frame")

# Full screen is 1920x1080
# Start 20 px from the left and 20 px from the top
x, y = 350, 140
w, h = 50, 50

crop = frame[y:y+h, x:x+w]

cv2.imwrite("switch_crop.png", crop)
print("Saved switch_crop.png")
