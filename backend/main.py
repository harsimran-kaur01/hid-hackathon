import time
import uuid
import json
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from models_interface import detect_spoof, identify_face
    from person3_identity.identity import enroll_person, get_recognizer
except ModuleNotFoundError:
    from backend.models_interface import detect_spoof, identify_face
    from backend.person3_identity.identity import enroll_person, get_recognizer
try:
    from decision_engine import make_decision
    from audit import init_db, log_decision
except ModuleNotFoundError:
    from backend.decision_engine import make_decision
    from backend.audit import init_db, log_decision

# Simple mode flag (will become more intelligent later)
CURRENT_MODE = "online"

app = FastAPI(title="EchoGate Backend – Person 4", version="0.1.0")

# Allow React frontend to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()
get_recognizer().load_gallery(Path(__file__).with_name("gallery.pkl"))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "EchoGate-Person4",
        "mode": CURRENT_MODE
    }

@app.post("/verify")
async def verify(
    image: Optional[UploadFile] = File(None),
    bbox: str = Form(...),
    frames: Optional[List[UploadFile]] = File(None),
):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    # ----- Validate inputs -----
    uploads = frames or ([image] if image else [])
    if not uploads:
        raise HTTPException(status_code=400, detail="At least one image is required")
    if any(not upload.content_type or not upload.content_type.startswith("image/") for upload in uploads):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        bbox_data = json.loads(bbox)
        required_keys = {"x", "y", "w", "h"}
        if not required_keys.issubset(bbox_data.keys()):
            raise ValueError("bbox missing required keys")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid bbox JSON. Expected {x,y,w,h}")

    frame_bytes = [await upload.read() for upload in uploads]
    image_bytes = frame_bytes[-1]

    spoof_result = detect_spoof(image_bytes, bbox_data, frame_bytes)
    identity_result = identify_face(image_bytes, bbox_data)

    # ----- Decision -----
    decision_result = make_decision(spoof_result, identity_result)

    # ----- Timing -----
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # ----- Build response -----
    response = {
        "decision": decision_result["decision"],
        "reason": decision_result["reason"],
        "spoof": spoof_result,
        "identity": identity_result,
        "latency_ms": latency_ms,
        "mode": "online",          # will become dynamic later
        "request_id": request_id
    }

    # ----- Audit -----
    log_decision(response)

    return response

@app.post("/enroll")
async def enroll(
    name: str = Form(...),
    image: UploadFile = File(...)
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    image_bytes = await image.read()
    decoded = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if decoded is None:
        raise HTTPException(status_code=400, detail="Unable to decode image")
    clean_name = name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Name must not be empty")
    if not enroll_person(clean_name, decoded):
        raise HTTPException(status_code=422, detail="No face found in image")
    get_recognizer().save_gallery(Path(__file__).with_name("gallery.pkl"))
    return {
        "ok": True,
        "message": f"Enrolled {clean_name} successfully",
        "name": clean_name
    }

@app.post("/set-mode")
def set_mode(mode: str = Form(...)):
    global CURRENT_MODE
    if mode not in ("online", "offline"):
        raise HTTPException(400, "mode must be 'online' or 'offline'")
    CURRENT_MODE = mode
    return {"mode": CURRENT_MODE}