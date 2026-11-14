export const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const TIMEOUT_MS = 5000;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const newId = () =>
  crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);

const MOCKS = [
  { decision: "ALLOW", reason: "Live person, identity verified, gate permitted",
    spoof: { label: "genuine", score: 0.97 }, identity: { name: "Priya", similarity: 0.82 },
    authorization: { allowed: true, role: "Staff", policy_source: "central",
      signature_valid: true, proof_bound: true } },
  { decision: "STEP_UP", reason: "Low confidence: poor lighting",
    spoof: { label: "genuine", score: 0.61 }, identity: { name: "Priya", similarity: 0.55 },
    authorization: { allowed: null, role: "Staff", policy_source: "cached",
      signature_valid: true, proof_bound: true } },
  { decision: "DENY", reason: "Spoof detected (screen replay)",
    spoof: { label: "spoof", score: 0.08 }, identity: { name: null, similarity: 0.0 },
    authorization: { allowed: false, policy_source: "central", proof_bound: false } },
];
let mockIndex = 0;

/**
 * Send one frame + face box for an access decision.
 * Extra fields (gate_id, request_id) are sent for Person 4's authorization and proof binding;
 * FastAPI ignores form fields it does not declare, so this is safe either way.
 */
export async function verify(blob, bbox, gateId = "main-gate") {
  const t0 = performance.now();
  const requestId = newId();
  if (USE_MOCK) {
    await sleep(600);
    const m = MOCKS[mockIndex++ % MOCKS.length];
    return { ...m, request_id: requestId, latency_ms: Math.round(performance.now() - t0), mode: "online" };
  }
  const fd = new FormData();
  fd.append("image", blob, "frame.jpg");
  fd.append("bbox", JSON.stringify(bbox));
  fd.append("gate_id", gateId);
  fd.append("request_id", requestId);

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${API}/verify`, { method: "POST", body: fd, signal: ctrl.signal });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();
    return {
      ...data,
      request_id: data.request_id ?? requestId,
      spoof: data.spoof ?? { label: "unknown", score: 0 },
      identity: data.identity ?? { name: null, similarity: 0 },
      authorization: data.authorization ?? null,
      latency_ms: data.latency_ms ?? Math.round(performance.now() - t0),
    };
  } catch (e) {
    if (e.name === "AbortError") throw new Error("Backend did not answer within 5 s");
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

/** Register one photo for a person. */
export async function enroll(name, blob) {
  if (USE_MOCK) { await sleep(400); return { ok: true }; }
  const fd = new FormData();
  fd.append("name", name);
  fd.append("image", blob, "enroll.jpg");
  const res = await fetch(`${API}/enroll`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`Enroll failed (${res.status})`);
  return res.json();
}

/**
 * Backend reachability + optional status details.
 * If /health returns JSON, these optional keys are shown in the header:
 *   mode ("online" | "offline"), pending_sync (number), policy_expires_at (string)
 */
export async function checkHealth() {
  if (USE_MOCK) return { ok: true, info: { mode: "online" } };
  try {
    const r = await fetch(`${API}/health`, { cache: "no-store" });
    if (!r.ok) return { ok: false, info: null };
    let info = null;
    try { info = await r.json(); } catch { /* plain 200 is fine */ }
    return { ok: true, info };
  } catch {
    return { ok: false, info: null };
  }
}
