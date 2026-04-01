import os
import sys
import pickle
import cv2
import face_recognition

# Database dosyası
DB_PATH = "face_db.pkl"


def load_database():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "rb") as f:
        return pickle.load(f)


def save_database(db):
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)


def register_face():
    name = input("Kayıt için adınızı girin: ").strip()
    if not name:
        print("Geçerli bir isim girin.")
        return

    print("Kamera açılıyor. Yüzünüzü çerçeveye hizalayın. Her yüz için 5 kare alınacak.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera açılamadı.")
        return

    encodings = []
    frame_count = 0

    while frame_count < 5:
        ret, frame = cap.read()
        if not ret:
            print("Kare okunamadı.")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        if len(boxes) == 1:
            encoding = face_recognition.face_encodings(rgb, boxes)[0]
            encodings.append(encoding)
            frame_count += 1
            cv2.putText(frame, f"Captured {frame_count}/5", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        elif len(boxes) > 1:
            cv2.putText(frame, "Lutfen sadece bir yuz gosterin", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Yuz bulunamadi", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        cv2.imshow("Register Face", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Kayit islemi iptal edildi.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(encodings) < 1:
        print("Yuz algilanamadi. Yeniden deneyin.")
        return

    db = load_database()
    db[name] = encodings
    save_database(db)
    print(f"{name} icin yüz verisi kaydedildi, toplam {len(encodings)} encoding.")


def login_face():
    db = load_database()
    if not db:
        print("Veritabanında kayıtlı kullanıcı bulunmuyor. Önce kayıt olun.")
        return

    known_names = list(db.keys())
    known_encodings = []
    for name in known_names:
        known_encodings.extend(db[name])

    print("Kamera açılıyor. Yüzünüzü tanımlamak için bekleyin...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera açılamadı.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kare okunamadı.")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)

        for box in boxes:
            top, right, bottom, left = box
            face_encoding = face_recognition.face_encodings(rgb, [box])[0]
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            match_name = "Unknown"
            if any(matches):
                best_match_index = int(face_distances.argmin())
                if matches[best_match_index]:
                    # En iyi eşleşmenin hangi kişiye ait olduğuna karar ver
                    # bilginin doğru isimle eşlenmesi için birden fazla encoding taşınıyor.
                    # known_names listesi ile index leri hesaplayalım.
                    # Burada kişi birden fazla encoding olabilir.
                    cumulative_encodings = 0
                    for person_name in known_names:
                        person_count = len(db[person_name])
                        if best_match_index < cumulative_encodings + person_count:
                            match_name = person_name
                            break
                        cumulative_encodings += person_count

            color = (0, 255, 0) if match_name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, match_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow("Login Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Face Recognition Phase 3 Backend\n")
    print("1 - Register user")
    print("2 - Login user")
    choice = input("Seciminizi yapin (1/2): ").strip()

    if choice == "1":
        register_face()
    elif choice == "2":
        login_face()
    else:
        print("Gecersiz secim.")
        sys.exit(0)
