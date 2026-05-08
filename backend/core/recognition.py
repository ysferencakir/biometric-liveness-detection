from collections import deque
import numpy as np
from core.detection import detect_faces, crop_face, compare_faces
from utils.constants import (
    FACE_MATCH_THRESHOLD,
    MIN_CONSECUTIVE_MATCHES,
    CONFIDENCE_WINDOW,
    MIN_REGISTRATION_FRAMES,
)


def find_best_match(face_region: np.ndarray, db: dict) -> tuple[str | None, float]:
    """
    Verilen yüz bölgesini veritabanındaki tüm kayıtlarla karşılaştırır.
    Dönüş: (en iyi eşleşen isim veya None, güven skoru)
    """
    best_name = None
    best_score = 0.0

    for name, frames in db.items():
        for entry in frames:
            stored = entry.get("frame", entry) if isinstance(entry, dict) else entry
            score = compare_faces(face_region, stored)
            if score > best_score:
                best_score = score
                best_name = name

    return best_name, best_score


def recognize_from_frames(frames: list[np.ndarray], db: dict) -> tuple[str | None, str]:
    """
    Frame listesinden yüz tanıma yapar.
    Ardışık CONFIDENCE_WINDOW frame boyunca ortalama skor eşiği geçerse
    ve MIN_CONSECUTIVE_MATCHES art arda eşleşme sağlanırsa giriş onaylanır.

    Dönüş: (tanınan_kullanıcı veya None, mesaj)
    """
    if not db:
        return None, "Veritabanında kayıtlı kullanıcı yok"

    consecutive = 0
    last_match = None
    confidence_history: deque[float] = deque(maxlen=CONFIDENCE_WINDOW)

    for frame in frames:
        from utils.image import to_grayscale
        gray = to_grayscale(frame)
        faces = detect_faces(gray)

        if not faces:
            consecutive = 0
            continue

        x, y, w, h = faces[0]
        face_region = crop_face(gray, x, y, w, h)
        name, score = find_best_match(face_region, db)

        confidence_history.append(score)
        avg_score = float(np.mean(confidence_history))

        if name and avg_score > FACE_MATCH_THRESHOLD:
            if name == last_match:
                consecutive += 1
            else:
                consecutive = 1
                last_match = name

            if consecutive >= MIN_CONSECUTIVE_MATCHES:
                return last_match, f"Hoşgeldiniz: {last_match} (güven: {avg_score:.2f})"
        else:
            consecutive = 0
            last_match = None

    return None, "Yüz tanınamadı"


def extract_face_frames(frames: list[np.ndarray]) -> tuple[list[dict], str | None]:
    """
    Frame listesinden yüz bölgelerini çıkarır, kayıt için saklar.
    Dönüş: (yüz veri listesi, hata mesajı veya None)
    """
    from utils.image import to_grayscale
    face_data = []

    for i, frame in enumerate(frames):
        gray = to_grayscale(frame)
        faces = detect_faces(gray)
        if faces:
            x, y, w, h = faces[0]
            region = crop_face(gray, x, y, w, h)
            face_data.append({"frame": region.copy(), "width": w, "height": h})

    if len(face_data) < MIN_REGISTRATION_FRAMES:
        return [], (
            f"Yetersiz veri: minimum {MIN_REGISTRATION_FRAMES} kare gerekli, "
            f"{len(face_data)} alındı"
        )

    return face_data, None
