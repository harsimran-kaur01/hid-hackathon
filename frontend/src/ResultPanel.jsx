const STYLE = {
  ALLOW:   { cls: "allow", title: "Access allowed" },
  STEP_UP: { cls: "stepup", title: "Extra verification needed" },
  DENY:    { cls: "deny", title: "Access denied" },
};
const pct = (n) => `${Math.round((n ?? 0) * 100)}%`;

export default function ResultPanel({ result, checking }) {
  if (!result) {
    return (
      <div className="result idle">
        <h1>{checking ? "Checking…" : "Waiting for a face"}</h1>
        <p className="reason">Biometric results appear here.</p>
      </div>
    );
  }
  const s = STYLE[result.decision] ?? STYLE.DENY;
  const fast = result.latency_ms <= 2000;
  return (
    <div className={`result ${s.cls}`}>
      <h1>{s.title}</h1>
      <p className="reason">{result.reason}</p>

      <div className="meters">
        <div>
          <span>Liveness: {result.spoof.label}</span>
          <div className="bar"><i style={{ width: pct(result.spoof.score) }} /></div>
          <b>{pct(result.spoof.score)}</b>
        </div>
        <div>
          <span>Identity: {result.identity.name ?? "Unknown"}</span>
          <div className="bar"><i style={{ width: pct(result.identity.similarity) }} /></div>
          <b>{pct(result.identity.similarity)}</b>
        </div>
      </div>

      <p className="latency">
        Decision time {(result.latency_ms / 1000).toFixed(2)} s {fast ? "(within 2 s)" : "(over 2 s)"}
        {checking ? " · updating…" : ""}
      </p>
      {result.decision === "STEP_UP" && (
        <p className="hint">Move to better light, face the camera directly and hold still.</p>
      )}
    </div>
  );
}
