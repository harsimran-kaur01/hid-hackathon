export default function AuditLog({ entries }) {
  return (
    <div className="panel">
      <h3>Recent decisions</h3>
      {entries.length === 0 ? (
        <p className="hint">No attempts yet.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Time</th><th>Decision</th><th>Person</th><th>Mode</th><th>Time taken</th></tr>
          </thead>
          <tbody>
            {entries.slice(0, 6).map((e, i) => (
              <tr key={i} className={e.decision.toLowerCase()}>
                <td>{e.time}</td><td>{e.decision}</td>
                <td>{e.name ?? "Unknown"}</td><td>{e.mode ?? "-"}</td><td>{e.latency} ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
