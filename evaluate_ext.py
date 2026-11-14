# evaluate_ext.py -- runs your detector on external videos in data_ext/<folder>/*.mp4
import cv2, glob, os, time, csv, json
from collections import defaultdict
from spoof_detector import detect_spoof, liveness_verdict

WIN, START = 1.2, 1.0  # seconds: window length, offset into the video
LIVE_WORDS = ("live", "real", "genuine")


def read_window(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    start = int(START * fps) if total > int((START + WIN) * fps) else 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = []
    for _ in range(int(WIN * fps)):
        ok, f = cap.read()
        if not ok:
            break
        h, w = f.shape[:2]
        if w > 640:
            f = cv2.resize(f, (640, int(h * 640 / w)))
        frames.append(f)
    cap.release()
    return frames


rows = defaultdict(list)
out = csv.writer(open("eval_ext_results.csv", "w", newline=""))
out.writerow(["folder", "file", "status", "score", "verdict", "ms", "cues"])
for path in sorted(glob.glob("data_ext/*/*.*")):
    folder = os.path.basename(os.path.dirname(path))
    frames = read_window(path)
    if len(frames) < 8:
        continue
    t = time.time()
    r = detect_spoof(frames)
    ms = int((time.time() - t) * 1000)
    v = liveness_verdict(r)
    rows[folder].append((v, r["liveness_score"], ms))
    out.writerow(
        [
            folder,
            os.path.basename(path),
            r["status"],
            r["liveness_score"],
            v,
            ms,
            json.dumps(r["cues"]),
        ]
    )
    print(
        f"{folder[:28]:28s} {os.path.basename(path)[:18]:18s} {r['status']:11s} {r['liveness_score']:.2f} {v}"
    )

print(f"\n{'folder':30s}{'n':>4s}{'ALLOW%':>8s}{'DENY%':>7s}{'STEP%':>7s}{'avg':>6s}")
for k, rs in sorted(rows.items()):
    n = len(rs)
    tag = "LIVE " if any(w in k.lower() for w in LIVE_WORDS) else "SPOOF"
    f = lambda x: sum(v == x for v, _, _ in rs) / n * 100
    print(
        f"{k[:30]:30s}{n:4d}{f('ALLOW'):8.0f}{f('DENY'):7.0f}{f('STEP-UP'):7.0f}{sum(s for _, s, _ in rs) / n:6.2f}  {tag}"
    )
print("\nSPOOF rows: ALLOW% = false accept rate.  LIVE rows: ALLOW% should be high.")
