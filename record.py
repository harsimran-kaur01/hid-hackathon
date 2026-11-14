# record.py  -- records labelled 1.2 s clips to data/<label>/<person>_<n>.mp4
# keys: l=live  i=impostor (live, not enrolled)  p=print  s=screen replay  v=video replay  m=mask  q=quit
import cv2, os, time

DURATION, COUNTDOWN = 1.2, 2.0
LABELS = {
    ord("l"): "live",
    ord("i"): "impostor",
    ord("p"): "print",
    ord("s"): "screen",
    ord("v"): "video",
    ord("m"): "mask",
}

person = input("Your name (no spaces): ").strip().lower() or "anon"
cap = cv2.VideoCapture(int(os.getenv("CAM", "0")))


def show(frame, text, color=(0, 255, 0)):
    f = frame.copy()
    cv2.putText(f, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.imshow("record", f)
    cv2.waitKey(1)


while True:
    ok, frame = cap.read()
    if not ok:
        print("Camera not working. Try:  $env:CAM=1; python record.py")
        break
    show(frame, "l live | i impostor | p print | s screen | v video | m mask | q quit")
    k = cv2.waitKey(1) & 0xFF
    if k == ord("q"):
        break
    if k in LABELS:
        label = LABELS[k]
        t0 = time.time()
        while time.time() - t0 < COUNTDOWN:  # time to get into position
            ok, frame = cap.read()
            show(
                frame,
                f"GET READY: {label} ({COUNTDOWN - (time.time() - t0):.1f}s)",
                (0, 200, 255),
            )
        frames, t0 = [], time.time()
        while time.time() - t0 < DURATION:  # recording: move or tilt now
            ok, frame = cap.read()
            frames.append(frame)
            show(frame, f"REC {label}: turn/tilt slowly", (0, 0, 255))
        os.makedirs(f"data/{label}", exist_ok=True)
        n = len([x for x in os.listdir(f"data/{label}") if x.startswith(person)]) + 1
        path = f"data/{label}/{person}_{n}.mp4"
        h, w = frames[0].shape[:2]
        fps = max(5, len(frames) / DURATION)
        vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        for f in frames:
            vw.write(f)
        vw.release()
        print("saved", path, f"({len(frames)} frames)")

cap.release()
cv2.destroyAllWindows()
