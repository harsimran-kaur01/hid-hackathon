# app.py
import json
import base64
import numpy as np
import cv2
from spoof_detector import detect_spoof


def _decode_frames(event):
    body = event.get("body", "{}")
    if isinstance(body, str):
        body = json.loads(body)

    frames_b64 = body.get("frames", [])
    if not frames_b64:
        # Fallback to single image
        frames_b64 = [body.get("image_base64", "")]

    frames = []
    for b64 in frames_b64:
        img_bytes = base64.b64decode(b64)
        arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is not None:
            frames.append(img)
    return frames


def lambda_handler(event, context):
    try:
        frames = _decode_frames(event)
        if not frames:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid frames provided"}),
            }

        # Call the video-aware detector
        result = detect_spoof(frames, return_evidence=True)
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
