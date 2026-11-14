import time
import uuid
import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from mocks import mock_spoof_detection, mock_identity_recognition
from decision_engine import make_decision
from audit import init_db, log_decision

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


@app.get("/health")
def health():
    return {"status": "ok", "service": "EchoGate-Person4"}


@app.post("/verify")
async def verify(
    image: UploadFile = File(...),
    bbox: str = Form(...)
):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    # ----- Validate inputs -----
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        bbox_data = json.loads(bbox)
        required_keys = {"x", "y", "w", "h"}
        if not required_keys.issubset(bbox_data.keys()):
            raise ValueError("bbox missing required keys")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid bbox JSON. Expected {x,y,w,h}")

    # Read image bytes
    image_bytes = await image.read()

    # ----- Run mocks (replace later with real models) -----
    spoof_result = mock_spoof_detection(image_bytes, bbox_data)
    identity_result = mock_identity_recognition(image_bytes, bbox_data)

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