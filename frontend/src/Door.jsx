import { useEffect, useState } from "react";

// stamp changes on every new result so a repeated ALLOW unlocks the door again
export default function Door({ decision, stamp }) {
  const [state, setState] = useState("LOCKED");

  useEffect(() => {
    if (decision === "ALLOW") {
      setState("UNLOCKED");
      const t = setTimeout(() => setState("LOCKED"), 3000);
      return () => clearTimeout(t);
    }
    setState(decision === "STEP_UP" ? "WAITING" : "LOCKED");
  }, [decision, stamp]);

  const label = {
    LOCKED: "Door locked",
    UNLOCKED: "Door unlocked",
    WAITING: "Waiting for verification",
  }[state];

  return (
    <div className={`door ${state.toLowerCase()}`}>
      <div className="door-leaf">{state === "UNLOCKED" ? "Open" : "Closed"}</div>
      <b>{label}</b>
    </div>
  );
}
