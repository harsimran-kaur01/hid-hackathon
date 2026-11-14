# test_webcam.py  -- keys: l=live  p=printed photo  s=screen replay  v=video replay  m=mask  q=quit
import cv2, time, csv, json
from spoof_detector import detect_spoof

cap = cv2.VideoCapture(0)
labels = {
    ord("l"): "live",
    ord("p"): "print",
    ord("s"): "screen",
    ord("v"): "video",
    ord("m"): "mask",
}
out = csv.writer(open("results.csv", "a", newline=""))
print("Press a label key, then slowly turn/tilt your head or the spoof for 2 seconds.")
while True:
    ok, f = cap.read()
    if not ok:
        break
    cv2.imshow("cam", f)
    k = cv2.waitKey(1) & 0xFF
    if k == ord("q"):
        break
    if k in labels:
        frames, t0 = [], time.time()
        while time.time() - t0 < 2.0:
            ok, f = cap.read()
            frames.append(f)
            cv2.imshow("cam", f)
            cv2.waitKey(1)
        t1 = time.time()
        r = detect_spoof(frames)
        ms = int((time.time() - t1) * 1000)
        print(labels[k], r, f"{ms}ms")
        out.writerow(
            [labels[k], r["status"], r["liveness_score"], json.dumps(r["cues"]), ms]
        )
cap.release()
