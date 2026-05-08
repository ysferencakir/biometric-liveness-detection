import cv2
import time

from face_db import load_database, save_database
from face_detection import face_cascade


def register_face_web(name, duration=15):
    """Web için yüz kayıt fonksiyonu"""
    try:
        if not name or name.strip() == "":
            return False, "Geçerli bir isim girin"

        name = name.strip()
        db = load_database()

        if name in db:
            return False, f"'{name}' zaten kayıtlı"

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return False, "Kamera açılamadı"

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        face_data = []
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_region = gray[y:y + h, x:x + w]
                face_data.append({'frame': face_region.copy(), 'timestamp': elapsed, 'width': w, 'height': h})

            if cv2.waitKey(30) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return False, "Kullanıcı tarafından iptal edildi"

        cap.release()
        cv2.destroyAllWindows()

        if len(face_data) >= 15:
            db = load_database()
            db[name] = face_data
            save_database(db)
            return True, f"{name} başarıyla kaydedildi! ({len(face_data)} kare)"
        return False, f"Yetersiz veri! Minimum 15 kare gerekli, {len(face_data)} alındı"

    except Exception as e:
        return False, f"Hata: {str(e)}"
