import cv2
import os
import pickle

# Database dosyası
DB_PATH = "faces_db.pkl"

def load_database():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "rb") as f:
        return pickle.load(f)

def save_database(db):
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)

# Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def register_face():
    try:
        name = input("\nAdınızı girin: ").strip()
        if not name:
            print("❌ Geçerli bir isim girin.")
            return
        
        print("\n📷 Kamera açılıyor...")
        print("   ℹ️  5 fotoğraf çekilecek, her biri arasında 15 saniye bekleme olacak.")
        print("   ℹ️  Q tuşuna basarak çıkabilirsiniz.\n")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Kamera açılamadı!")
            return
        
        faces_count = 0
        face_data = []
        last_capture_time = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Kare okunamadı.")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            time_diff = current_time - last_capture_time
            
            # Her 15 saniyede bir yüz çek (eğer algılanırsa)
            if len(faces) > 0 and time_diff >= 5.0:
                (x, y, w, h) = faces[0]  # İlk yüzü al
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                face_region = gray[y:y+h, x:x+w]
                face_data.append(face_region)
                faces_count += 1
                last_capture_time = current_time
                
                print(f"   ✓ Fotoğraf {faces_count}/5 çekildi!")
            
            # Yüz olup olmadığını göster
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Bilgi metni
            secs_until_next = max(0, int(15.0 - time_diff))
            status = f"Bekleme: {secs_until_next}s | Çekilen: {faces_count}/5 | Q=Çık"
            cv2.putText(frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("KAYIT MODU - Q ile çık", frame)
            
            # 5 fotoğraf çekildiyse, tamamlandı mesajı ve otomatik kapan
            if faces_count >= 5:
                print("\n✓ Kayıt Tamamlandı!\n")
                cap.release()
                cv2.destroyAllWindows()
                break
            
            if cv2.waitKey(100) & 0xFF == ord("q"):
                print("\n❌ Kayıt iptal edildi.\n")
                cap.release()
                cv2.destroyAllWindows()
                return
        
        cap.release()
        cv2.destroyAllWindows()
        
        if face_data and faces_count >= 5:
            db = load_database()
            db[name] = face_data
            save_database(db)
            print(f"✓ {name} başarıyla kaydedildi ({len(face_data)} fotoğraf).\n")
        
    except Exception as e:
        print(f"❌ Kayıt sırasında hata: {e}\n")
        cap.release()
        cv2.destroyAllWindows()

def login_face():
    try:
        db = load_database()
        if not db:
            print("\n❌ Kayıtlı kullanıcı yok. Önce kayıt olun.\n")
            return
        
        print("\n📷 Kamera açılıyor...")
        print("   ℹ️  Yüzünüzü kameraya gösterin.")
        print("   ℹ️  Q tuşuna basarak çıkabilirsiniz.\n")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Kamera açılamadı!\n")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Kare okunamadı.")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                face_region = gray[y:y+h, x:x+w]
                
                # Basit karşılaştırma: histogram benzerliği
                best_match = "Unknown"
                best_score = 0
                
                for name, stored_faces in db.items():
                    for stored_face in stored_faces:
                        # Histogram karşılaştırması
                        hist1 = cv2.calcHist([face_region], [0], None, [256], [0, 256])
                        hist2 = cv2.calcHist([stored_face], [0], None, [256], [0, 256])
                        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
                        
                        if score > best_score:
                            best_score = score
                            best_match = name
                
                color = (0, 255, 0) if best_match != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, best_match, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            cv2.putText(frame, "Q tusuna basarak cikabilirsiniz", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("GİRİŞ MODU - Q ile çık", frame)
            
            if cv2.waitKey(100) & 0xFF == ord("q"):
                print("\n✓ Giriş modundan çıkılıyor...\n")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"❌ Giriş sırasında hata: {e}\n")
        cap.release()
        cv2.destroyAllWindows()

def main():
    while True:
        print("\n" + "="*40)
        print("     YÜZ TANIMA SİSTEMİ (OpenCV)")
        print("="*40)
        print("  1 - Kayıt Ol")
        print("  2 - Giriş Yap")
        print("  3 - Çıkış")
        print("="*40)
        
        try:
            choice = input("Seçiminizi yapın (1/2/3): ").strip()
            
            if choice == "1":
                register_face()
            elif choice == "2":
                login_face()
            elif choice == "3":
                print("\n" + "="*40)
                print("✓ Program kapatılıyor... Hoşça kalın!")
                print("="*40 + "\n")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 1, 2 veya 3 seçin.\n")
        except KeyboardInterrupt:
            print("\n\n" + "="*40)
            print("✓ Program durduruluyor... Hoşça kalın!")
            print("="*40 + "\n")
            break
        except Exception as e:
            print(f"❌ Hata oluştu: {e}\n")

if __name__ == "__main__":
    main()
