# evaluate.py -- runs the detector on every saved clip and prints a per-attack table
import cv2, glob, os, time, csv, json
from collections import defaultdict
from spoof_detector import detect_spoof, liveness_verdict

SHOULD_ALLOW = {
    "live",
    "impostor",
}  # for LIVENESS, a live impostor face is still a live face
rows = defaultdict(list)
out = csv.writer(open("eval_results.csv", "w", newline=""))
out.writerow(["label", "file", "status", "score", "verdict", "detect_ms", "cues"])

for path in sorted(glob.glob("data/*/*.mp4")):
    label = path.replace("\\", "/").split("/")[1]
    cap = cv2.VideoCapture(path)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()
    t = time.time()
    r = detect_spoof(frames)
    ms = int((time.time() - t) * 1000)
    v = liveness_verdict(r)
    rows[label].append((v, r["liveness_score"], ms))
    out.writerow(
        [label, path, r["status"], r["liveness_score"], v, ms, json.dumps(r["cues"])]
    )
    print(
        f"{label:9s} {os.path.basename(path):14s} {r['status']:12s} score={r['liveness_score']:.2f}  {v}  {ms}ms"
    )

print("\n=== PER-SCENARIO RESULTS (liveness only) ===")
print(
    f"{'scenario':10s}{'n':>4s}{'ALLOW%':>8s}{'DENY%':>8s}{'STEP-UP%':>10s}{'avg score':>11s}{'avg ms':>8s}"
)
for label, rs in rows.items():
    n = len(rs)
    a = sum(v == "ALLOW" for v, _, _ in rs) / n * 100
    d = sum(v == "DENY" for v, _, _ in rs) / n * 100
    s = sum(v == "STEP-UP" for v, _, _ in rs) / n * 100
    print(
        f"{label:10s}{n:4d}{a:8.0f}{d:8.0f}{s:10.0f}{sum(x for _, x, _ in rs) / n:11.2f}{sum(x for _, _, x in rs) / n:8.0f}"
    )
print(
    "\nFor live: want high ALLOW%.  For print/screen/video/mask: ALLOW% is your false-accept rate (want 0)."
)
print("Total decision time = 1200 ms capture + avg ms above. Must be under 2000.")
