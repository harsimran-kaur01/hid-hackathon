# eval_stream.py  usage: python eval_stream.py <repo> [N per folder]   e.g. python eval_stream.py marcusmball/face-anti-spoofing-dataset 3
import sys, os, cv2, time, csv, json, collections
from huggingface_hub import list_repo_files, hf_hub_download
from spoof_detector import detect_spoof, liveness_verdict

REPO = sys.argv[1] if len(sys.argv) > 1 else "marcusmball/face-anti-spoofing-dataset"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3
EXT = (".mp4", ".avi", ".mov", ".webm", ".mkv")
WIN, START = 1.2, 1.0
LIVE_WORDS = ("live", "real", "genuine")


def read_frames(src):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return []
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    for _ in range(int(START * fps)):  # skip intro (sequential read works for streams)
        if not cap.grab():
            break
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


files = [
    f for f in list_repo_files(REPO, repo_type="dataset") if f.lower().endswith(EXT)
]
groups = collections.defaultdict(list)
for f in files:
    groups[os.path.dirname(f)].append(f)

rows = collections.defaultdict(list)
out = csv.writer(open("eval_stream_results.csv", "w", newline=""))
out.writerow(["folder", "file", "status", "score", "verdict", "cues"])
for g, fs in sorted(groups.items()):
    for f in fs[:N]:
        url = f"https://huggingface.co/datasets/{REPO}/resolve/main/{f.replace(' ', '%20')}"
        frames = read_frames(url)
        if len(frames) < 8:  # streaming failed -> download this one file
            try:
                frames = read_frames(hf_hub_download(REPO, f, repo_type="dataset"))
            except Exception as e:
                print("skip", f, e)
                continue
        if len(frames) < 8:
            print("skip (too short)", f)
            continue
        r = detect_spoof(frames)
        v = liveness_verdict(r)
        rows[g].append((v, r["liveness_score"]))
        out.writerow(
            [
                g,
                os.path.basename(f),
                r["status"],
                r["liveness_score"],
                v,
                json.dumps(r["cues"]),
            ]
        )
        print(
            f"{g[:34]:34s} {os.path.basename(f)[:16]:16s} {r['status']:11s} {r['liveness_score']:.2f} {v}"
        )

print(f"\n{'folder':36s}{'n':>3s}{'ALLOW%':>8s}{'DENY%':>7s}{'STEP%':>7s}{'avg':>6s}")
tot = acc = 0
for k, rs in sorted(rows.items()):
    n = len(rs)
    fr = lambda x: sum(v == x for v, _ in rs) / n * 100
    spoof = not any(w in k.lower() for w in LIVE_WORDS)
    if spoof:
        tot += n
        acc += sum(v == "ALLOW" for v, _ in rs)
    print(
        f"{k[:36]:36s}{n:3d}{fr('ALLOW'):8.0f}{fr('DENY'):7.0f}{fr('STEP-UP'):7.0f}{sum(s for _, s in rs) / n:6.2f}"
    )
if tot:
    print(
        f"\nOVERALL FALSE ACCEPT on external attacks: {acc}/{tot} = {acc / tot * 100:.0f}%"
    )
