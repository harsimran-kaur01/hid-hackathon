import { useState } from "react";
import FaceCamera from "./FaceCamera";
import { enroll } from "./api";

const TARGET = 5;

export default function Enroll() {
  const [name, setName] = useState("");
  const [count, setCount] = useState(0);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  async function handleCapture(blob) {
    if (!name.trim()) { setMsg("Enter a name first."); return; }
    setBusy(true);
    setMsg("");
    try {
      await enroll(name.trim(), blob);
      setCount((c) => c + 1);
      setMsg("Photo saved.");
    } catch (e) {
      setMsg(e.message);
    }
    setBusy(false);
  }

  const done = count >= TARGET;
  return (
    <div className="enroll">
      <input
        placeholder="Person's name"
        value={name}
        onChange={(e) => { setName(e.target.value); setCount(0); setMsg(""); }}
      />
      <p>Photos saved: {count} of {TARGET}</p>
      {done ? (
        <div className="result allow">
          <h1>{name} is enrolled</h1>
          <button className="primary" onClick={() => { setName(""); setCount(0); setMsg(""); }}>
            Enroll another person
          </button>
        </div>
      ) : (
        <FaceCamera
          onCapture={handleCapture}
          disabled={busy || !name.trim()}
          buttonLabel="Save photo"
          hint="Change your head angle and lighting slightly between photos."
        />
      )}
      {msg && <p className="status">{msg}</p>}
    </div>
  );
}
