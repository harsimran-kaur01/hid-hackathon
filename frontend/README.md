# EchoGate UI (Person 1)

## Run it (needs Node.js 18+ and internet on first load)
```
npm install
npm run dev
```
Open http://localhost:5173 in Chrome or Edge and allow camera access.

## Backend connection
Edit `.env`:
- `VITE_USE_MOCK=false`  -> talk to the real FastAPI backend
- `VITE_USE_MOCK=true`   -> fake ALLOW / STEP_UP / DENY cycle, no backend needed
- `VITE_API_URL=http://localhost:8000`
Restart `npm run dev` after changing `.env`.

## FastAPI must provide
- `POST /verify`  form fields: `image` (JPEG file), `bbox` (JSON string {x,y,w,h})
  returns `{decision, reason, spoof:{label,score}, identity:{name,similarity}, latency_ms, mode}`
  where decision is ALLOW | DENY | STEP_UP
- `POST /enroll`  form fields: `name`, `image` (JPEG file)  -> any JSON
- `GET /health`   -> 200 when online (drives the ONLINE/OFFLINE badge)
- CORS enabled for http://localhost:5173:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])
```

## Notes
- The face detector (MediaPipe) loads its model from a CDN, so the laptop needs internet
  the first time. For a fully offline demo, load the page once online before going offline;
  the browser may cache it, but test this before the demo.
- If your /verify field names differ, only `src/api.js` needs to change.
