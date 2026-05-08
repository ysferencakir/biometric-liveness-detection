import cv2
import time
import numpy as np

from face_db import load_database
from face_detection import face_cascade, compare_faces


def login_face_web():
    """Web için yüz tanıma fonksiyonu"""
    try:
        db = load_database()
        if not db:
            return None, "Veritabanında kayıt bulunmuyor"

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, "Kamera açılamadı"

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        recognized_frames = 0
        last_recognized = None
        confidence_history = []
        start_time = time.time()
        MAX_DURATION = 30

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            if time.time() - start_time > MAX_DURATION:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            best_match = None
            best_confidence = 0

            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_region = gray[y:y + h, x:x + w]

                for name, face_data_list in db.items():
                    for face_data in face_data_list:
                        stored_face = face_data.get('frame', face_data) if isinstance(face_data, dict) else face_data
                        confidence = compare_faces(face_region, stored_face)

                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = name

                confidence_history.append(best_confidence)
                if len(confidence_history) > 10:
                    confidence_history.pop(0)

                avg_confidence = np.mean(confidence_history) if confidence_history else 0

                if best_match and avg_confidence > 0.5:
                    recognized_frames += 1
                    last_recognized = best_match

                    if recognized_frames >= 3:
                        cap.release()
                        cv2.destroyAllWindows()
                        return last_recognized, f"Hoşgeldiniz: {last_recognized} (Güven: {avg_confidence:.2f})"
                else:
                    recognized_frames = 0

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        return None, "Yüz tanınamadı"

    except Exception as e:
        return None, f"Hata: {str(e)}"
