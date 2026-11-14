# enroll.py -- press e to enroll someone, q to quit
import cv2, os, time, numpy as np
from identity import embed_frames

os.makedirs("enrolled", exist_ok=True)
name = input("Name to enroll (no spaces): ").strip().lower()
cap = cv2.VideoCapture(int(os.getenv("CAM", "0")))


def show(frame, text, color=(0, 255, 0)):
    f = frame.copy()
    cv2.putText(f, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("enroll", f)
    cv2.waitKey(1)


while True:
    ok, frame = cap.read()
    if not ok:
        break
    show(frame, f"press e to enroll '{name}' | q quit")
    k = cv2.waitKey(1) & 0xFF
    if k == ord("q"):
        break
    if k == ord("e"):
        t0 = time.time()
        while time.time() - t0 < 2:
            ok, frame = cap.read()
            show(frame, "Look at camera...", (0, 200, 255))
        frames, t0 = [], time.time()
        while time.time() - t0 < 2:
            ok, frame = cap.read()
            frames.append(frame)
            show(frame, "Recording: slightly turn your head", (0, 0, 255))
        emb = embed_frames(frames, n=12)
        if emb is None:
            print("No face found, try again with better light")
        else:
            np.save(f"enrolled/{name}.npy", emb)
            print("enrolled", name)
            break
cap.release()
cv2.destroyAllWindows()
