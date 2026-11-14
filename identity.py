# identity.py
import os, glob, numpy as np
from insightface.app import FaceAnalysis

MATCH_T, REJECT_T = (
    0.45,
    0.30,
)  # cosine similarity: >=MATCH_T same person, <REJECT_T different (tune later)
_app = None


def _get_app():
    global _app
    if _app is None:
        _app = FaceAnalysis(
            name=os.getenv("FACE_MODEL", "buffalo_l"),
            providers=["CPUExecutionProvider"],
            allowed_modules=["detection", "recognition"],
        )
        _app.prepare(ctx_id=-1, det_size=(320, 320))
    return _app


def embed(frame):
    faces = _get_app().get(frame)
    if not faces:
        return None
    f = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    return f.normed_embedding


def embed_frames(frames, n=8):
    idx = np.linspace(0, len(frames) - 1, min(n, len(frames))).astype(int)
    embs = [e for e in (embed(frames[i]) for i in idx) if e is not None]
    if not embs:
        return None
    m = np.mean(embs, axis=0)
    return m / np.linalg.norm(m)


def load_gallery(folder="enrolled"):
    return {
        os.path.splitext(os.path.basename(p))[0]: np.load(p)
        for p in glob.glob(os.path.join(folder, "*.npy"))
    }


def match_identity(frames):
    gallery = load_gallery()
    if not gallery:
        return {
            "status": "no_gallery",
            "user_id": None,
            "identity_score": 0.0,
            "verdict": "DENY",
        }
    e = embed_frames(frames)
    if e is None:
        return {
            "status": "no_face",
            "user_id": None,
            "identity_score": 0.0,
            "verdict": "STEP-UP",
        }
    sims = {name: float(np.dot(e, g)) for name, g in gallery.items()}
    best = max(sims, key=sims.get)
    s = sims[best]
    verdict = "MATCH" if s >= MATCH_T else ("NO_MATCH" if s < REJECT_T else "UNSURE")
    return {
        "status": "ok",
        "user_id": best if verdict == "MATCH" else None,
        "closest": best,
        "identity_score": round(s, 3),
        "verdict": verdict,
        "all_scores": {k: round(v, 3) for k, v in sims.items()},
    }
