from time import monotonic

import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
print("Camera opened")
start = monotonic()
while monotonic() - start < 5:
    ret, frame = cap.read()
    if not ret:
        print("Frame not captured")
        break
    print(f"Frame shape: {frame.shape}")
    # show
    cv2.imshow("test", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
print("Done")
