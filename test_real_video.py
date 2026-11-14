# test_real_video.py
import cv2
import requests
import numpy as np
from spoof_detector import detect_spoof

# Public video with actual human movement
video_url = "https://github.com/intel-iot-devkit/sample-videos/raw/master/face-demographics-walking.mp4"

print("Downloading real walking video...")
r = requests.get(video_url, stream=True)
with open("walking.mp4", "wb") as f:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)

cap = cv2.VideoCapture("walking.mp4")
frames = []
# Grab 10 frames spread out over time to capture movement
for i in range(10):
    ret, frame = cap.read()
    if not ret:
        break
    if i % 3 == 0:  # Skip every 3rd frame to show movement
        # Resize to simulate a face crop
        frame = cv2.resize(frame, (300, 300))
        frames.append(frame)
cap.release()

print(f"Extracted {len(frames)} frames. Testing...")
result = detect_spoof(frames, return_evidence=True)
print(result)
