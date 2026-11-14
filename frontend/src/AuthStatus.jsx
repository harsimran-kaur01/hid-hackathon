// Shows what the backend's authorization engine decided. Every field is optional:
// rows only appear if Person 4's /verify response includes them under "authorization".
const yn = (v) => (v === true ? "Yes" : v === false ? "No" : "Pending");

export default function AuthStatus({ result }) {
  const a = result?.authorization;
  const rows = [];
  if (a) {
    if ("allowed" in a) rows.push(["Gate permission", yn(a.allowed)]);
    if (a.role) rows.push(["Role", a.role]);
    if (a.policy_source) rows.push(["Policy source", a.policy_source === "cached" ? "Cached (offline)" : "Central server"]);
    if (a.policy_expires_at) rows.push(["Policy valid until", a.policy_expires_at]);
    if ("signature_valid" in a) rows.push(["Policy signature", a.signature_valid ? "Verified" : "Invalid"]);
    if ("proof_bound" in a) rows.push(["Evidence bound to request", yn(a.proof_bound)]);
  }
  if (result?.mode) rows.push(["Decided in", `${result.mode} mode`]);
  if (result?.request_id) rows.push(["Request ID", result.request_id.slice(0, 8)]);

  return (
    <div className="panel">
      <h3>Authorization</h3>
      {!result ? (
        <p className="hint">Nothing to show yet.</p>
      ) : rows.length === 0 ? (
        <p className="hint">The backend did not send authorization details.</p>
      ) : (
        <dl>
          {rows.map(([k, v]) => (
            <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
          ))}
        </dl>
      )}
    </div>
  );
}
