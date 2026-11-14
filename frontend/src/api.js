export const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const MOCKS = [
  { decision: "ALLOW", reason: "Live person, identity verified",
    spoof: { label: "genuine", score: 0.97 }, identity: { name: "Priya", similarity: 0.82 } },
  { decision: "STEP_UP", reason: "Low confidence: poor lighting",
    spoof: { label: "genuine", score: 0.61 }, identity: { name: "Priya", similarity: 0.55 } },
  { decision: "DENY", reason: "Spoof detected (screen replay)",
    spoof: { label: "spoof", score: 0.08 }, identity: { name: null, similarity: 0.0 } },
];
let mockIndex = 0;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Send one captured frame + face box for an access decision. */
export async function verify(blob, bbox) {
  const t0 = performance.now();
  if (USE_MOCK) {
    await sleep(600);
    const m = MOCKS[mockIndex++ % MOCKS.length];
    return { ...m, latency_ms: Math.round(performance.now() - t0), mode: "online" };
  }
  const fd = new FormData();
  fd.append("image", blob, "frame.jpg");
  fd.append("bbox", JSON.stringify(bbox));
  const res = await fetch(`${API}/verify`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`Server error ${res.status}`);
  const data = await res.json();
  return {
    ...data,
    spoof: data.spoof ?? { label: "unknown", score: 0 },
    identity: data.identity ?? { name: null, similarity: 0 },
    latency_ms: data.latency_ms ?? Math.round(performance.now() - t0),
  };
}

/** Register one photo for a person. */
export async function enroll(name, blob) {
  if (USE_MOCK) {
    await sleep(400);
    return { ok: true };
  }
  const fd = new FormData();
  fd.append("name", name);
  fd.append("image", blob, "enroll.jpg");
  const res = await fetch(`${API}/enroll`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(`Enroll failed (${res.status})`);
  return res.json();
}

/** Backend reachability check used by the ONLINE/OFFLINE badge. */
export async function checkHealth() {
  if (USE_MOCK) return true;
  try {
    const r = await fetch(`${API}/health`, { cache: "no-store" });
    return r.ok;
  } catch {
    return false;
  }
}
