import { useRef, useState } from "react";
import FaceCamera from "./FaceCamera";
import ResultPanel from "./ResultPanel";
import AuthStatus from "./AuthStatus";
import Door from "./Door";
import AuditLog from "./AuditLog";
import Enroll from "./Enroll";
import { verify } from "./api";
import { useOnline } from "./useOnline";
import { GATES, LIVE_INTERVAL_MS } from "./config";

export default function App() {
  const [tab, setTab] = useState("verify");
  const [gate, setGate] = useState(GATES[0].id);
  const [live, setLive] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [stamp, setStamp] = useState(0);
  const [error, setError] = useState("");
  const [log, setLog] = useState([]);
  const busyRef = useRef(false);
  const lastLog = useRef({ key: "", t: 0 });
  const { ok: online, info } = useOnline();

  async function handleCapture(blob, bbox) {
    if (busyRef.current) return; // one request at a time
    busyRef.current = true;
    setBusy(true);
    setError("");
    try {
      const r = await verify(blob, bbox, gate);
      setResult(r);
      setStamp((s) => s + 1);

      // Live scan sends many frames: only log when something changes or every 5 s
      const key = `${r.decision}|${r.identity.name}`;
      const now = Date.now();
      if (key !== lastLog.current.key || now - lastLog.current.t > 5000) {
        lastLog.current = { key, t: now };
        setLog((l) => [
          { time: new Date().toLocaleTimeString(), decision: r.decision, name: r.identity.name,
            mode: r.mode, latency: r.latency_ms },
          ...l,
        ]);
      }
    } catch (e) {
      setError(`${e.message}. Check that the backend is running.`);
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  }

  function handleFaceChange(found) {
    // In live mode, clear the result when the person walks away so the door re-locks
    if (!found && live) setResult(null);
  }

  const offlineMode = !online ? "unreachable" : info?.mode === "offline" ? "local" : null;

  return (
    <div className="app">
      <header>
        <h2>EchoGate</h2>
        <nav>
          <button onClick={() => setTab("verify")} disabled={tab === "verify"}>Verify</button>
          <button onClick={() => setTab("enroll")} disabled={tab === "enroll"}>Enroll</button>
        </nav>
        <div className="status-group">
          <span className={`badge ${offlineMode ? "off" : "on"}`}>
            {offlineMode === "unreachable" ? "OFFLINE · backend unreachable"
              : offlineMode === "local" ? "OFFLINE MODE · local policy" : "ONLINE"}
          </span>
          {online && info?.pending_sync > 0 && (
            <span className="badge sync">{info.pending_sync} pending sync</span>
          )}
        </div>
      </header>

      {tab === "enroll" ? (
        <Enroll />
      ) : (
        <main>
          <section className="left">
            <div className="controls">
              <label>
                Gate{" "}
                <select value={gate} onChange={(e) => setGate(e.target.value)}>
                  {GATES.map((g) => <option key={g.id} value={g.id}>{g.label}</option>)}
                </select>
              </label>
              <label className="toggle">
                <input type="checkbox" checked={live} onChange={(e) => setLive(e.target.checked)} />
                Live scan
              </label>
            </div>
            <FaceCamera
              onCapture={handleCapture}
              disabled={busy}
              captureSequence
              auto={live}
              autoMs={LIVE_INTERVAL_MS}
              onFaceChange={handleFaceChange}
            />
            {error && <p className="error">{error}</p>}
          </section>

          <aside>
            <ResultPanel result={result} checking={busy} />
            <div className="row">
              <AuthStatus result={result} />
              <Door decision={result?.decision ?? null} stamp={stamp} />
            </div>
            <AuditLog entries={log} />
          </aside>
        </main>
      )}
    </div>
  );
}
