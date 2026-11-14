import { useEffect, useState } from "react";
import { checkHealth } from "./api";

export function useOnline() {
  const [online, setOnline] = useState(true);
  useEffect(() => {
    let alive = true;
    const run = async () => {
      const ok = await checkHealth();
      if (alive) setOnline(ok);
    };
    run();
    const id = setInterval(run, 3000);
    return () => { alive = false; clearInterval(id); };
  }, []);
  return online;
}
