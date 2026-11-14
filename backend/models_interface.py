"""Adapters that connect the backend contract to the real model modules."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable

import cv2
import numpy as np

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = Path(__file__).resolve().parent
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("MODEL_LOCAL_PATH", str(REPOSITORY_ROOT / "MiniFASNetV2.pth"))

from spoof_detector import detect_spoof as run_liveness
from spoof_detector import liveness_verdict
from person3_identity.identity import identify_face as run_identity


def _decode(image_bytes: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image")
    return image


def detect_spoof(
    image_bytes: bytes,
    bbox: Dict[str, int],
    frame_bytes: Iterable[bytes] | None = None,
) -> Dict[str, Any]:
    """Run Person 2's liveness detector and map it to the API contract."""
    del bbox
    frames = [_decode(data) for data in (frame_bytes or [image_bytes])]
    result = run_liveness(frames)
    verdict = liveness_verdict(result)
    label = {"ALLOW": "genuine", "DENY": "spoof"}.get(verdict, "uncertain")
    return {
        "label": label,
        "score": float(result.get("liveness_score", 0.0)),
        "status": result.get("status"),
        "cues": result.get("cues", {}),
    }


def identify_face(image_bytes: bytes, bbox: Dict[str, int]) -> Dict[str, Any]:
    """Run Person 3's ArcFace recognizer and map it to the API contract."""
    del bbox
    result = run_identity(_decode(image_bytes))
    name = result.get("identity")
    return {
        "name": None if name in (None, "unknown") else name,
        "similarity": float(result.get("confidence", 0.0)),
        "status": result.get("status"),
    }