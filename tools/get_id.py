import cv2

for i in range(10):
    cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
    ok, frame = cap.read()
    if ok:
        print(f"Device {i} works, frame shape = {frame.shape}")
    cap.release()
