import cv2
import numpy as np
from insightface.app import FaceAnalysis
from pathlib import Path
import pickle

class IdentityRecognizer:
    def __init__(self, ctx_id=-1, det_size=(640, 640)):
        """
        ctx_id = -1 → CPU,  0 → GPU
        """
        self.app = FaceAnalysis(
            name="buffalo_sc",
            providers=["CPUExecutionProvider"]
        )
        self.app.prepare(ctx_id=ctx_id, det_size=det_size)
        
        self.gallery = {}          # name → list of embeddings
        self.threshold = 0.45      # cosine similarity threshold

    def get_embedding(self, image_bgr):
        """Returns the best face embedding or None"""
        faces = self.app.get(image_bgr)
        if len(faces) == 0:
            return None
        # take the largest face
        face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]))
        emb = face.embedding
        # Force L2 normalization
        emb = emb / np.linalg.norm(emb)
        return emb

    def enroll(self, name: str, image_bgr):
        emb = self.get_embedding(image_bgr)
        if emb is None:
            return False
        if name not in self.gallery:
            self.gallery[name] = []
        self.gallery[name].append(emb)
        return True

    def identify(self, image_bgr):
        """
        Returns: (name, similarity) or ("unknown", 0.0)
        """
        emb = self.get_embedding(image_bgr)
        if emb is None:
            return "unknown", 0.0

        best_name = "unknown"
        best_sim = -1.0

        for name, embs in self.gallery.items():
            for g_emb in embs:
                sim = float(np.dot(emb, g_emb))
                if sim > best_sim:
                    best_sim = sim
                    best_name = name

        if best_sim < self.threshold:
            return "unknown", best_sim
        return best_name, best_sim

    def save_gallery(self, path="gallery.pkl"):
        with open(path, "wb") as f:
            pickle.dump(self.gallery, f)

    def load_gallery(self, path="gallery.pkl"):
        if Path(path).exists():
            with open(path, "rb") as f:
                self.gallery = pickle.load(f)


# ========== Interface for Person 4 ==========
recognizer = None

def get_recognizer():
    global recognizer
    if recognizer is None:
        recognizer = IdentityRecognizer(ctx_id=-1)
    return recognizer

def identify_face(face_image):
    """
    Main function Person 4 will call.
    Input : BGR numpy array (OpenCV image)
    Output: dict with identity, confidence, status
    """
    rec = get_recognizer()
    name, score = rec.identify(face_image)
    
    return {
        "identity": name,
        "confidence": round(float(score), 4),
        "status": "match" if name != "unknown" else "no_match"
    }

def enroll_person(name, face_image):
    """Helper to enroll a person"""
    rec = get_recognizer()
    success = rec.enroll(name, face_image)
    return success