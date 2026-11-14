# test_video.py
import cv2
import requests
import numpy as np
from spoof_detector import detect_spoof

# A public test video of a real person
video_url = "https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-female-and-male.mp4"

print("Downloading test video...")
r = requests.get(video_url, stream=True)
with open("test_video.mp4", "wb") as f:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)

# Extract 10 frames
cap = cv2.VideoCapture("test_video.mp4")
frames = []
for _ in range(10):
    ret, frame = cap.read()
    if not ret:
        break
    # Resize to simulate a face crop
    frame = cv2.resize(frame, (300, 300))
    frames.append(frame)
cap.release()

print(f"Extracted {len(frames)} frames. Testing...")
result = detect_spoof(frames, return_evidence=True)
print(result)
