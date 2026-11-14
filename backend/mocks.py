import random
from typing import Dict, Any

def mock_spoof_detection(image_bytes: bytes, bbox: Dict) -> Dict[str, Any]:
    """
    Temporary mock for Person 2.
    Replace this function with real MiniFASNetV2 later.
    """
    # Simulate realistic behaviour
    roll = random.random()
    if roll > 0.85:
        return {"label": "spoof", "score": round(random.uniform(0.75, 0.98), 3)}
    elif roll > 0.70:
        return {"label": "uncertain", "score": round(random.uniform(0.45, 0.65), 3)}
    else:
        return {"label": "genuine", "score": round(random.uniform(0.82, 0.99), 3)}


def mock_identity_recognition(image_bytes: bytes, bbox: Dict) -> Dict[str, Any]:
    """
    Temporary mock for Person 3.
    Replace this function with real ArcFace later.
    """
    names = ["Priya", "Arjun", "Sneha", "Rahul", None, None]
    name = random.choice(names)
    
    if name is None:
        return {"name": None, "similarity": round(random.uniform(0.30, 0.55), 3)}
    else:
        return {"name": name, "similarity": round(random.uniform(0.72, 0.96), 3)}