"""
This is the ONLY file Person 2 and Person 3 need to touch later.
Replace the two functions below with their real implementations.
"""

from typing import Dict, Any
from mocks import mock_spoof_detection, mock_identity_recognition


def detect_spoof(image_bytes: bytes, bbox: Dict[str, int]) -> Dict[str, Any]:
    """
    Person 2 (Anti-spoofing) will replace this function.
    
    Expected return format:
    {
        "label": "genuine" | "spoof" | "uncertain",
        "score": float          # 0.0 – 1.0
    }
    """
    return mock_spoof_detection(image_bytes, bbox)


def identify_face(image_bytes: bytes, bbox: Dict[str, int]) -> Dict[str, Any]:
    """
    Person 3 (ArcFace Identity) will replace this function.
    
    Expected return format:
    {
        "name": str | None,
        "similarity": float     # 0.0 – 1.0
    }
    """
    return mock_identity_recognition(image_bytes, bbox)