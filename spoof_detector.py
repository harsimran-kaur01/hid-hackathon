# spoof_detector.py
import os, cv2, numpy as np, torch, torch.nn.functional as F
import mediapipe as mp
from collections import OrderedDict
from models.MiniFASNet import MiniFASNetV2

_model = None
_mesh = None

R_EYE = [33, 160, 158, 133, 153, 144]
L_EYE = [362, 385, 387, 263, 373, 380]

PLANAR_LO, PLANAR_RANGE = 0.15, 0.5
MOIRE_LO, MOIRE_RANGE = 40, 120
LIVE_T, SPOOF_T = 0.8, 0.4
MIN_MOTION = 1.5


def _load_model():
    global _model
    if _model is not None:
        return _model
    m = MiniFASNetV2(conv6_kernel=(5, 5), num_classes=3, img_channel=3)
    ck = torch.load(
        os.getenv("MODEL_LOCAL_PATH", "MiniFASNetV2.pth"), map_location="cpu"
    )
    ck = OrderedDict((k.replace("module.", "", 1), v) for k, v in ck.items())
    m.load_state_dict(ck)
    m.eval()
    _model = m
    return m


def _get_mesh():
    global _mesh
    if _mesh is None:
        _mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
    return _mesh


def _landmarks(frame):
    h, w = frame.shape[:2]
    res = _get_mesh().process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if not res.multi_face_landmarks:
        return None
    return np.array(
        [[p.x * w, p.y * h] for p in res.multi_face_landmarks[0].landmark], np.float32
    )


def _crop_2_7(frame, pts, scale=2.7):
    h, w = frame.shape[:2]
    x1, y1 = pts.min(0)
    x2, y2 = pts.max(0)
    bw, bh = x2 - x1, y2 - y1
    s = min((h - 1) / bh, (w - 1) / bw, scale)
    nw, nh = bw * s, bh * s
    cx, cy = x1 + bw / 2, y1 + bh / 2
    l, t = cx - nw / 2, cy - nh / 2
    r, b = cx + nw / 2, cy + nh / 2
    if l < 0:
        r -= l
        l = 0
    if t < 0:
        b -= t
        t = 0
    if r > w - 1:
        l -= r - (w - 1)
        r = w - 1
    if b > h - 1:
        t -= b - (h - 1)
        b = h - 1
    l, t, r, b = [int(max(0, v)) for v in (l, t, r, b)]
    return frame[t : b + 1, l : r + 1]


def _cnn_live_prob(crop):
    img = cv2.resize(crop, (80, 80)).astype(np.float32)
    x = torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0)
    with torch.no_grad():
        p = F.softmax(_load_model()(x), 1)[0].numpy()
    return float(p[1])


def _moire_score(face):
    g = cv2.resize(cv2.cvtColor(face, cv2.COLOR_BGR2GRAY), (128, 128)).astype(
        np.float32
    )
    g -= g.mean()
    win = np.hanning(128)[:, None] * np.hanning(128)[None, :]
    mag = np.abs(np.fft.fftshift(np.fft.fft2(g * win)))
    yy, xx = np.indices(mag.shape)
    r = np.hypot(yy - 64, xx - 64)
    ring = mag[(r > 20) & (r < 60)]
    peakiness = ring.max() / (np.median(ring) + 1e-6)
    return float(np.clip((peakiness - MOIRE_LO) / MOIRE_RANGE, 0, 1))


def _ear(pts, idx):
    p = pts[idx]
    return (np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])) / (
        2 * np.linalg.norm(p[0] - p[3]) + 1e-6
    )


def _planarity(lms):
    ref = lms[0]
    fw = np.ptp(ref[:, 0]) + 1e-6
    res, mot = [], []
    for cur in lms[1:]:
        H, _ = cv2.findHomography(ref, cur, 0)
        if H is None:
            continue
        proj = cv2.perspectiveTransform(ref[None], H)[0]
        res.append(np.linalg.norm(proj - cur, axis=1).mean() / fw * 100)
        mot.append(np.linalg.norm(cur - ref, axis=1).mean() / fw * 100)
    if not res:
        return None, 0.0
    return float(np.mean(res)), float(np.max(mot))


def detect_spoof(frames):
    if not frames:
        return {"status": "no_face", "liveness_score": 0.0, "cues": {}}

    step = max(1, len(frames) // 15)
    frames = frames[::step]

    lms, crops = [], []
    for f in frames:
        p = _landmarks(f)
        if p is not None:
            lms.append(p)
            crops.append(_crop_2_7(f, p))
    if len(lms) < max(5, len(frames) // 2):
        return {"status": "no_face", "liveness_score": 0.0, "cues": {}}

    idx = np.linspace(0, len(crops) - 1, min(6, len(crops))).astype(int)
    cnn = float(np.mean([_cnn_live_prob(crops[i]) for i in idx]))
    moire = float(np.mean([_moire_score(crops[i]) for i in idx]))

    ears = np.array([(_ear(p, R_EYE) + _ear(p, L_EYE)) / 2 for p in lms])
    blink = bool(ears.min() < 0.75 * np.median(ears))

    resid, motion = _planarity(lms)
    enough_motion = resid is not None and motion >= MIN_MOTION
    planar_live = (
        float(np.clip((resid - PLANAR_LO) / PLANAR_RANGE, 0, 1))
        if enough_motion
        else None
    )

    if planar_live is None:
        score = 0.75 * cnn + 0.25 * (1 - moire)
        status = "need_motion"
    else:
        score = 0.45 * cnn + 0.35 * planar_live + 0.20 * (1 - moire)
        status = "ok"
    if blink:
        score = min(1.0, score + 0.05)

    return {
        "status": status,
        "liveness_score": round(score, 3),
        "cues": {
            "cnn_live": round(cnn, 3),
            "moire": round(moire, 3),
            "blink": blink,
            "planar_residual_pct": None if resid is None else round(resid, 3),
            "motion_pct": round(motion, 2),
            "planar_live": None if planar_live is None else round(planar_live, 3),
        },
    }


def liveness_verdict(r):
    if r["status"] in ("no_face", "need_motion"):
        return "STEP-UP"
    s = r["liveness_score"]
    if s >= LIVE_T:
        return "ALLOW"
    if s < SPOOF_T:
        return "DENY"
    return "STEP-UP"
