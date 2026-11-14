# verify_live.py -- press SPACE to run a check, q to quit. Logs every attempt to audit_log.csv
import cv2, os, time, csv
from spoof_detector import detect_spoof, liveness_verdict
from identity import match_identity

CAPTURE = 1.2
cap = cv2.VideoCapture(int(os.getenv("CAM", "0")))
log = csv.writer(open("audit_log.csv", "a", newline=""))


def show(frame, lines, color=(0, 255, 0), wait=1):
    f = frame.copy()
    for i, t in enumerate(lines):
        cv2.putText(f, t, (10, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.imshow("kiosk", f)
    cv2.waitKey(wait)


def decide(live_v, ident):
    if live_v == "DENY":
        return "DENY", "spoof detected"
    if ident["verdict"] == "NO_MATCH":
        return "DENY", "identity mismatch"
    if live_v == "ALLOW" and ident["verdict"] == "MATCH":
        return "ALLOW", "live + identity match"
    return "STEP-UP", "low confidence"


while True:
    ok, frame = cap.read()
    if not ok:
        break
    show(frame, ["SPACE = check | q = quit"])
    k = cv2.waitKey(1) & 0xFF
    if k == ord("q"):
        break
    if k == 32:
        t0 = time.time()
        while time.time() - t0 < 1.5:  # time to get in position
            ok, frame = cap.read()
            show(frame, ["Get ready..."], (0, 200, 255))
        frames, t0 = [], time.time()
        while time.time() - t0 < CAPTURE:
            ok, frame = cap.read()
            frames.append(frame)
            show(frame, ["Look at camera, turn head slowly"], (0, 0, 255))
        live = detect_spoof(frames)
        live_v = liveness_verdict(live)
        ident = match_identity(frames)
        decision, reason = decide(live_v, ident)
        total_ms = int((time.time() - t0) * 1000)
        print(
            f"{decision:8s} | liveness={live['liveness_score']} ({live_v}, {live['status']}) | "
            f"identity={ident['identity_score']} ({ident['verdict']}, closest={ident.get('closest')}) | {total_ms}ms"
        )
        log.writerow(
            [
                time.strftime("%H:%M:%S"),
                decision,
                reason,
                live["liveness_score"],
                live_v,
                ident["identity_score"],
                ident["verdict"],
                ident.get("closest"),
                total_ms,
            ]
        )
        col = {"ALLOW": (0, 255, 0), "DENY": (0, 0, 255), "STEP-UP": (0, 200, 255)}[
            decision
        ]
        show(
            frame,
            [
                f"{decision}: {reason}",
                f"liveness {live['liveness_score']}  identity {ident['identity_score']}",
                f"{total_ms} ms",
            ],
            col,
            wait=2500,
        )
cap.release()
cv2.destroyAllWindows()
