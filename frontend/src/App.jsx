import { useState } from "react";
import FaceCamera from "./FaceCamera";
import ResultPanel from "./ResultPanel";
import Door from "./Door";
import AuditLog from "./AuditLog";
import Enroll from "./Enroll";
import { verify } from "./api";
import { useOnline } from "./useOnline";

export default function App() {
  const [tab, setTab] = useState("verify");
  const [phase, setPhase] = useState("idle"); // idle | checking | result
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [log, setLog] = useState([]);
  const online = useOnline();

  async function handleCapture(blob, bbox) {
    setPhase("checking");
    setError("");
    try {
      const r = await verify(blob, bbox);
      setResult(r);
      setLog((l) => [
        { time: new Date().toLocaleTimeString(), decision: r.decision,
          name: r.identity.name, latency: r.latency_ms },
        ...l,
      ]);
      setPhase("result");
    } catch (e) {
      setError(`${e.message}. Check that the backend is running.`);
      setPhase("idle");
    }
  }

  return (
    <div className="app">
      <header>
        <h2>EchoGate</h2>
        <nav>
          <button onClick={() => setTab("verify")} disabled={tab === "verify"}>Verify</button>
          <button onClick={() => setTab("enroll")} disabled={tab === "enroll"}>Enroll</button>
        </nav>
        <span className={`badge ${online ? "on" : "off"}`}>{online ? "ONLINE" : "OFFLINE"}</span>
      </header>

      {tab === "enroll" ? (
        <Enroll />
      ) : (
        <main>
          <section className="left">
            {phase === "result" ? (
              <ResultPanel result={result} onReset={() => setPhase("idle")} />
            ) : (
              <>
                <FaceCamera onCapture={handleCapture} disabled={phase === "checking"} />
                {phase === "checking" && <p className="status">Checking…</p>}
                {error && <p className="error">{error}</p>}
              </>
            )}
            <AuditLog entries={log} />
          </section>
          <aside>
            <Door decision={phase === "result" ? result?.decision : null} />
          </aside>
        </main>
      )}
    </div>
  );
}
