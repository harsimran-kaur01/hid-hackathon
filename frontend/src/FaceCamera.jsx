import { useEffect, useRef, useState } from "react";
import { FaceDetector, FilesetResolver } from "@mediapipe/tasks-vision";

const WASM = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL =
  "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite";

export default function FaceCamera({ onCapture, disabled, buttonLabel = "Verify", hint }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const boxRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [faceFound, setFaceFound] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let raf, stream, detector;
    let stopped = false;

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
        try {
          detector = await FaceDetector.createFromOptions(fileset, {
            baseOptions: { modelAssetPath: MODEL, delegate: "GPU" },
            runningMode: "VIDEO",
            minDetectionConfidence: 0.6,
          });
        } catch {
          detector = await FaceDetector.createFromOptions(fileset, {
            baseOptions: { modelAssetPath: MODEL, delegate: "CPU" },
            runningMode: "VIDEO",
            minDetectionConfidence: 0.6,
          });
        }
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
        if (det) {
          const b = det.boundingBox;
          boxRef.current = { x: b.originX, y: b.originY, w: b.width, h: b.height };
          ctx.strokeStyle = "#34d399";
          ctx.lineWidth = 4;
          ctx.strokeRect(b.originX, b.originY, b.width, b.height);
          setFaceFound(true);
        } else {
          boxRef.current = null;
          setFaceFound(false);
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

  function capture() {
    const video = videoRef.current;
    const bbox = boxRef.current;
    if (!bbox) return;
    const c = document.createElement("canvas");
    c.width = video.videoWidth;
    c.height = video.videoHeight;
    c.getContext("2d").drawImage(video, 0, 0); // not mirrored: models get the true image
    c.toBlob((blob) => onCapture(blob, bbox), "image/jpeg", 0.85);
  }

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
      <button className="primary" onClick={capture} disabled={!faceFound || disabled}>
        {buttonLabel}
      </button>
    </div>
  );
}
