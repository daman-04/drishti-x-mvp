import cv2
cap = cv2.VideoCapture('backend-ai/sample.mp4')
count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(f"Ended at {count} frames.")
        cap.release()
        cap = cv2.VideoCapture('backend-ai/sample.mp4')
        ret, frame = cap.read()
        print(f"Reopened. Read first frame: {ret}")
        break
    count += 1
