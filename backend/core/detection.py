import cv2
import numpy as np
from utils.constants import HAAR_SCALE_FACTOR, HAAR_MIN_NEIGHBORS

# Modül yüklendiğinde bir kez başlatılır
_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_faces(gray_frame: np.ndarray) -> list[tuple]:
    """
    Gri tonlamalı görüntüde yüzleri tespit eder.
    Dönüş: [(x, y, w, h), ...] listesi
    """
    faces = _face_cascade.detectMultiScale(
        gray_frame, HAAR_SCALE_FACTOR, HAAR_MIN_NEIGHBORS
    )
    return list(faces) if len(faces) > 0 else []


def crop_face(gray_frame: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    return gray_frame[y : y + h, x : x + w]


def compare_faces(face1: np.ndarray, face2: np.ndarray) -> float:
    """
    İki yüz bölgesini histogram benzerliğiyle karşılaştırır.
    Dönüş: 0.0–1.0 arası benzerlik skoru (1.0 = tam eşleşme)

    Bhattacharyya mesafesi kullanılır; düşük mesafe = yüksek benzerlik.
    Hızlı ama ışık değişimine duyarlı — üretim için encoding tabanlı
    yöntemlerle (FaceNet, ArcFace) değiştirilmesi önerilir.
    """
    try:
        if face1.shape != face2.shape:
            face2 = cv2.resize(face2, (face1.shape[1], face1.shape[0]))
        hist1 = cv2.calcHist([face1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([face2], [0], None, [256], [0, 256])
        distance = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
        return float(1 - distance)
    except Exception:
        return 0.0
