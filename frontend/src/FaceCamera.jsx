import { useEffect, useRef, useState } from "react";
import { FaceDetector, FilesetResolver } from "@mediapipe/tasks-vision";

const WASM = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL =
  "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite";

export default function FaceCamera({
  onCapture, disabled, buttonLabel = "Verify", hint,
  auto = false, autoMs = 1500, onFaceChange, captureSequence = false,
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const boxRef = useRef(null);
  const faceRef = useRef(false);
  const latest = useRef({});
  latest.current = { onCapture, disabled, onFaceChange };

  const [ready, setReady] = useState(false);
  const [faceFound, setFaceFound] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let raf, stream, detector;
    let stopped = false;

    async function makeDetector(fileset, delegate) {
      return FaceDetector.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: MODEL, delegate },
        runningMode: "VIDEO",
        minDetectionConfidence: 0.6,
      });
    }

    async function init() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: "user" },
          audio: false,
        });
        if (stopped) { stream.getTracks().forEach((t) => t.stop()); return; }
        videoRef.current.srcObject = stream;
        await videoRef.current.play();

        const fileset = await FilesetResolver.forVisionTasks(WASM);
        try { detector = await makeDetector(fileset, "GPU"); }
        catch { detector = await makeDetector(fileset, "CPU"); }
        if (stopped) return;
        setReady(true);
        loop();
      } catch (e) {
        setError(e.message || "Camera or face detector failed to load");
      }
    }

    function loop() {
      if (stopped) return;
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (video && canvas && video.readyState >= 2) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const det = detector.detectForVideo(video, performance.now()).detections[0];
        const found = Boolean(det);
        if (det) {
          const b = det.boundingBox;
          boxRef.current = { x: b.originX, y: b.originY, w: b.width, h: b.height };
          ctx.strokeStyle = "#34d399";
          ctx.lineWidth = 4;
          ctx.strokeRect(b.originX, b.originY, b.width, b.height);
        } else {
          boxRef.current = null;
        }
        if (found !== faceRef.current) {
          faceRef.current = found;
          setFaceFound(found);
          latest.current.onFaceChange?.(found);
        }
      }
      raf = requestAnimationFrame(loop);
    }

    init();
    return () => {
      stopped = true;
      cancelAnimationFrame(raf);
      stream?.getTracks().forEach((t) => t.stop());
      detector?.close();
    };
  }, []);

  function captureFrame() {
    const bbox = boxRef.current;
    const video = videoRef.current;
    if (!video || !bbox) return null;
    const c = document.createElement("canvas");
    c.width = video.videoWidth;
    c.height = video.videoHeight;
    c.getContext("2d").drawImage(video, 0, 0); // not mirrored: models get the true image
    return new Promise((resolve) => c.toBlob(resolve, "image/jpeg", 0.85));
  }

  async function capture() {
    const bbox = boxRef.current;
    if (!bbox) return;
    if (!captureSequence) {
      const blob = await captureFrame();
      if (blob) latest.current.onCapture(blob, bbox);
      return;
    }
    const frames = [];
    for (let i = 0; i < 8; i += 1) {
      const frame = await captureFrame();
      if (frame) frames.push(frame);
      if (i < 7) await new Promise((resolve) => setTimeout(resolve, 120));
    }
    if (frames.length) latest.current.onCapture(frames, bbox);
  }

  // Live scan: send a frame every autoMs while a face is visible and no request is running
  useEffect(() => {
    if (!auto) return;
    const id = setInterval(() => {
      if (boxRef.current && !latest.current.disabled) capture();
    }, autoMs);
    return () => clearInterval(id);
  }, [auto, autoMs]);

  if (error) return <p className="error">Camera problem: {error}. Allow camera access and reload.</p>;

  return (
    <div className="camera">
      <div className="camera-frame">
        <video ref={videoRef} playsInline muted className="mirror" />
        <canvas ref={canvasRef} className="mirror overlay" />
      </div>
      <p className="status">
        {!ready ? "Loading face detector…" : faceFound ? "Face detected" : "Position your face in view"}
      </p>
      {hint && <p className="hint">{hint}</p>}
      {!auto && (
        <button className="primary" onClick={capture} disabled={!faceFound || disabled}>
          {buttonLabel}
        </button>
      )}
    </div>
  );
}
