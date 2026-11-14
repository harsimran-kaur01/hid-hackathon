import { useEffect, useState } from "react";

export default function Door({ decision }) {
  const [state, setState] = useState("LOCKED");

  useEffect(() => {
    if (decision === "ALLOW") {
      setState("UNLOCKED");
      const t = setTimeout(() => setState("LOCKED"), 3000);
      return () => clearTimeout(t);
    }
    setState(decision === "STEP_UP" ? "WAITING" : "LOCKED");
  }, [decision]);

  return (
    <div className={`door ${state.toLowerCase()}`}>
      <div className="door-leaf">{state === "UNLOCKED" ? "Open" : "Closed"}</div>
      <b>{state === "WAITING" ? "Waiting for verification" : state === "UNLOCKED" ? "Door unlocked" : "Door locked"}</b>
    </div>
  );
}
