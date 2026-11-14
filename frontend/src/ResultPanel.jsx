const STYLE = {
  ALLOW:   { cls: "allow", title: "Access allowed" },
  STEP_UP: { cls: "stepup", title: "Extra verification needed" },
  DENY:    { cls: "deny", title: "Access denied" },
};

const pct = (n) => `${Math.round((n ?? 0) * 100)}%`;

export default function ResultPanel({ result, onReset }) {
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
        {result.mode ? ` · ${result.mode} mode` : ""}
      </p>

      {result.decision === "STEP_UP" && (
        <p className="hint">Move to better light, face the camera directly and try again.</p>
      )}
      <button className="primary" onClick={onReset}>
        {result.decision === "STEP_UP" ? "Capture again" : "Verify next person"}
      </button>
    </div>
  );
}
