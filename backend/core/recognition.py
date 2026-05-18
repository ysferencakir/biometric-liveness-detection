"""
Yüz tanıma modülü.

Backend önceliği (otomatik seçilir):
  1. deepface / Facenet  — en yüksek doğruluk (pip install deepface tf-keras)
  2. MediaPipe landmarks — ek bağımlılık gerektirmez, orta doğruluk

Her iki backend de aynı fonksiyon imzasını paylaşır.
"""
from collections import deque
from pathlib import Path

import cv2
import numpy as np

from utils.constants import (
    FACE_MATCH_THRESHOLD,
    MIN_CONSECUTIVE_MATCHES,
    CONFIDENCE_WINDOW,
    MIN_REGISTRATION_FRAMES,
    MODEL_PATH,
)

try:
    from deepface import DeepFace as _df
    _DF_OK = True
except ImportError:
    _df = None
    _DF_OK = False

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options as mp_base_options
    from mediapipe.tasks.python.vision.core import image as mp_image_module
    _MP_OK = Path(MODEL_PATH).exists()
except Exception:
    _MP_OK = False

_BACKEND = "deepface" if _DF_OK else ("mediapipe" if _MP_OK else "none")


def _get_landmarker():
    options = vision.FaceLandmarkerOptions(
        base_options=mp_base_options.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
    )
    return vision.FaceLandmarker.create_from_options(options)


def _landmarks_to_embedding(lm_list) -> np.ndarray | None:
    """
    MediaPipe NormalizedLandmark listesini 936-boyutlu normalize embedding'e çevirir.
    Normalizasyon: göz ortası merkez, göz mesafesi ölçek.
    """
    if not lm_list:
        return None
    pts = np.array([[lm.x, lm.y] for lm in lm_list], dtype=float)  # (468,2)

    # Gözlerin merkezi ve arası mesafe (ölçek referansı)
    # Sol göz iç köşe: 133, sağ göz iç köşe: 362
    left_inner  = pts[133]
    right_inner = pts[362]
    center = (left_inner + right_inner) / 2.0
    scale  = float(np.linalg.norm(right_inner - left_inner)) + 1e-6

    # Merkeze çek ve ölçekle
    pts = (pts - center) / scale          # (468,2)
    vec = pts.flatten()                   # (936,)
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > 0 else vec


def _frame_to_embedding(bgr_frame: np.ndarray) -> np.ndarray | None:
    """BGR frame'den yüz embedding çıkarır. Yüz yoksa None döner."""
    if _BACKEND == "deepface":
        return _deepface_embedding(bgr_frame)
    if _BACKEND == "mediapipe":
        return _mediapipe_embedding(bgr_frame)
    return None


def _deepface_embedding(bgr_frame: np.ndarray) -> np.ndarray | None:
    """DeepFace / Facenet ile 512-dim embedding."""
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        cv2.imwrite(tmp_path, bgr_frame)
        result = _df.represent(
            img_path=tmp_path,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="opencv",
            align=True,
        )
        os.unlink(tmp_path)
        if result:
            return np.array(result[0]["embedding"], dtype=float)
    except Exception:
        pass
    return None


def _mediapipe_embedding(bgr_frame: np.ndarray) -> np.ndarray | None:
    """MediaPipe 468 landmark → 936-dim normalize vektör."""
    rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    mp_img = mp_image_module.Image(mp_image_module.ImageFormat.SRGB, rgb)
    with _get_landmarker() as lm:
        result = lm.detect(mp_img)
    if not result.face_landmarks:
        return None
    return _landmarks_to_embedding(result.face_landmarks[0])


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# --------------------------------------------------------------------------- #
#  Kayıt                                                                        #
# --------------------------------------------------------------------------- #

def extract_face_frames(frames: list[np.ndarray]) -> tuple[list[dict], str | None]:
    """
    BGR frame listesinden yüz embedding çıkarır.
    DB formatı: [{"encoding": np.ndarray(936,)}, ...]
    """
    if not _MP_OK:
        return [], "MediaPipe yüklenemedi veya model dosyası bulunamadı"

    encodings: list[dict] = []
    for frame in frames:
        emb = _frame_to_embedding(frame)
        if emb is not None:
            encodings.append({"encoding": emb})

    if len(encodings) < MIN_REGISTRATION_FRAMES:
        return [], (
            f"Yetersiz veri: minimum {MIN_REGISTRATION_FRAMES} kare gerekli, "
            f"{len(encodings)} alındı"
        )
    return encodings, None


# --------------------------------------------------------------------------- #
#  Karşılaştırma                                                                #
# --------------------------------------------------------------------------- #

def find_best_match(face_encoding: np.ndarray, db: dict) -> tuple[str | None, float]:
    """
    936-boyutlu embedding'i DB kayıtlarıyla cosine similarity ile karşılaştırır.
    Dönüş: (en iyi eşleşen isim veya None, güven skoru 0–1)
    """
    best_name: str | None = None
    best_score: float = 0.0

    for name, entries in db.items():
        stored = [
            e["encoding"]
            for e in entries
            if isinstance(e, dict) and "encoding" in e
        ]
        if not stored:
            continue
        # Kayıtlı frame'lerin ortalamasına karşı karşılaştır
        ref = np.mean(stored, axis=0)
        score = _cosine_similarity(face_encoding, ref)
        if score > best_score:
            best_score = score
            best_name = name

    return best_name, best_score


# --------------------------------------------------------------------------- #
#  Tanıma                                                                       #
# --------------------------------------------------------------------------- #

def recognize_from_frames(
    frames: list[np.ndarray], db: dict
) -> tuple[str | None, float, str]:
    """
    BGR frame listesinden yüz tanıma yapar.
    Dönüş: (kullanıcı_adı | None, en_iyi_skor, mesaj)
    """
    if not _MP_OK:
        return None, 0.0, "MediaPipe yüklenemedi veya model dosyası bulunamadı"
    if not db:
        return None, 0.0, "Veritabanında kayıtlı kullanıcı yok"

    consecutive = 0
    last_match: str | None = None
    confidence_history: deque[float] = deque(maxlen=CONFIDENCE_WINDOW)

    for frame in frames:
        emb = _frame_to_embedding(frame)
        if emb is None:
            consecutive = 0
            continue

        name, score = find_best_match(emb, db)
        confidence_history.append(score)
        avg_score = float(np.mean(confidence_history))

        if name and avg_score > FACE_MATCH_THRESHOLD:
            if name == last_match:
                consecutive += 1
            else:
                consecutive = 1
                last_match = name
            if consecutive >= MIN_CONSECUTIVE_MATCHES:
                return last_match, avg_score, f"Hoşgeldiniz: {last_match} (güven: {avg_score:.2f})"
        else:
            consecutive = 0
            last_match = None

    fallback = float(np.mean(confidence_history)) if confidence_history else 0.0
    return None, fallback, "Yüz tanınamadı"
