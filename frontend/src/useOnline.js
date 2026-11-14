import { useEffect, useState } from "react";
import { checkHealth } from "./api";

export function useOnline() {
  const [state, setState] = useState({ ok: true, info: null });
  useEffect(() => {
    let alive = true;
    const run = async () => {
      const s = await checkHealth();
      if (alive) setState(s);
    };
    run();
    const id = setInterval(run, 3000);
    return () => { alive = false; clearInterval(id); };
  }, []);
  return state;
}
