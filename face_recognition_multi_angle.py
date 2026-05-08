import cv2
import os
import pickle
import numpy as np
from datetime import datetime
import time

# Database dosyası
DB_PATH = "faces_db_enhanced.pkl"

def load_database():
    """Veritabanını yükle"""
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, "rb") as f:
            return pickle.load(f)
    except:
        return {}

def save_database(db):
    """Veritabanını kaydet"""
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)
    print(f"✓ Veritabanı kaydedildi: {DB_PATH}")

# Haar Cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def calculate_face_angle(face_region):
    """Yüzün açısını tahmin etmek için basit bir metod"""
    try:
        # Yüz bölgesinin özelliklerini analiz et
        height, width = face_region.shape[:2]
        aspect_ratio = width / height if height > 0 else 1
        return aspect_ratio
    except:
        return 1.0

def register_face_enhanced():
    """
    ✨ GELİŞTİRİLMİŞ KAYIT MODU
    - Yüz video kaydı (sürekli çerçeve)
    - Farklı açılardan otomatik kaptür
    - Veri tabanına tüm kareler kaydedilir
    """
    try:
        print("\n" + "="*70)
        print("📷 GELİŞTİRİLMİŞ YÜZ KAYIT MODU".center(70))
        print("="*70)
        
        name = input("\n👤 Adınızı girin: ").strip()
        if not name:
            print("❌ Geçerli bir isim girin.")
            return
        
        db = load_database()
        if name in db:
            response = input(f"⚠️  '{name}' zaten kayıtlı. Üzerine yazılsın mı? (e/h): ").lower()
            if response != 'e':
                print("❌ İşlem iptal edildi.\n")
                return
        
        print("\n📋 TALIMATLAR:")
        print("   1️⃣  Kamera açıldıktan sonra BAŞLA tuşuna (SPACE) basın")
        print("   2️⃣  Yüzünüzü KALıN KONUMA getirin")
        print("   3️⃣  Baş aşağı/yukarı döndürün")
        print("   4️⃣  Sola/sağa döndürün")
        print("   5️⃣  Çeşitli açılardan geçin")
        print("   6️⃣  İşlem 15 saniye sürecek, Q ile iptal edebilirsiniz\n")
        
        print("⏳ Kamera açılıyor...\n")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Kamera açılamadı!")
            return
        
        # Kamera ayarları
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 20)
        
        face_data = []
        recording = False
        record_start_time = None
        RECORDING_DURATION = 15  # 15 saniye
        
        print("🎥 KAMERA HAZIR - SPACE'e basarak başlayın...\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Kare okunamadı.")
                break
            
            frame = cv2.flip(frame, 1)  # Aynayı çevir
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Zaman kontrolü
            if recording and record_start_time is not None:
                elapsed = time.time() - record_start_time
                if elapsed >= RECORDING_DURATION:
                    recording = False
                    print(f"\n✓ Kayıt tamamlandı! {len(face_data)} kare kaydedildi.\n")
                    cap.release()
                    cv2.destroyAllWindows()
                    break
            
            # Yüz algılandıysa
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                
                # Yüz bölgesini çek
                face_region = gray[y:y+h, x:x+w]
                
                if recording and len(face_region) > 0:
                    # Her karede kaydedilen yüz verisini sakla
                    face_data.append({
                        'frame': face_region.copy(),
                        'timestamp': time.time() - record_start_time if record_start_time else 0,
                        'width': w,
                        'height': h
                    })
                
                # Yüz dikdörtgeni çiz
                color = (0, 255, 0) if recording else (0, 255, 255)
                thickness = 3 if recording else 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
                
                # Yüz boyutu bilgisi
                cv2.putText(frame, f"Boyut: {w}x{h}", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Durum göstergesi
            status_color = (0, 255, 0) if recording else (0, 255, 255)
            status_text = "KAYIT DEVAM EDİYOR" if recording else "HAZIR - SPACE ile başlat"
            
            cv2.putText(frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            if recording and record_start_time:
                elapsed = time.time() - record_start_time
                remaining = max(0, RECORDING_DURATION - elapsed)
                cv2.putText(frame, f"Kalan: {remaining:.1f}s | Kareler: {len(face_data)}", (10, 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "SPACE=Başla | Q=Çık", (10, 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            cv2.imshow("YÜZ KAYIT - Farklı Açılardan Döndürün", frame)
            
            key = cv2.waitKey(30) & 0xFF
            
            if key == ord(' '):  # SPACE
                if not recording:
                    recording = True
                    record_start_time = time.time()
                    print("▶️  KAYIT BAŞLADI! Yüzü döndürmeye başlayın...\n")
            
            if key == ord('q') or key == ord('Q'):
                print("\n❌ İşlem iptal edildi.\n")
                cap.release()
                cv2.destroyAllWindows()
                return
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Verileri kaydet
        if len(face_data) >= 15:  # En az 15 kare
            db = load_database()
            db[name] = face_data
            save_database(db)
            print(f"✅ {name} başarıyla kaydedildi!")
            print(f"   📊 Toplam kaydedilen kareler: {len(face_data)}")
            print(f"   💾 Veritabanı dosyası: {DB_PATH}\n")
            return True
        else:
            print(f"❌ Yetersiz veri! Minimum 15 kare gerekli, {len(face_data)} alındı.\n")
            return False
            
    except Exception as e:
        print(f"❌ Kayıt sırasında hata: {e}\n")
        return False

def compare_faces(face1, face2):
    """İki yüzü karşılaştır (Euclidean distance)"""
    try:
        if face1.shape != face2.shape:
            # Boyutu eşitle
            face2 = cv2.resize(face2, (face1.shape[1], face1.shape[0]))
        
        # Histogram eşleştirmesi yap
        hist1 = cv2.calcHist([face1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([face2], [0], None, [256], [0, 256])
        
        # Histogram karşılaştırması
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
        return 1 - similarity  # 0-1 arası değer (1 = eşleşme, 0 = farklı)
    except:
        return 0

def login_face_enhanced():
    """
    ✨ GELİŞTİRİLMİŞ GİRİŞ MODU
    - Tüm kaydedilen açılarla karşılaştırma
    - Daha doğru tanıma
    """
    try:
        print("\n" + "="*70)
        print("🔐 GELİŞTİRİLMİŞ YÜZ TANIMA MODU".center(70))
        print("="*70 + "\n")
        
        db = load_database()
        if not db:
            print("❌ Veritabanında kayıt bulunmuyor. Önce kayıt olun.\n")
            return
        
        print("📷 Kamera açılıyor. Lütfen yüzünüzü kameraya gösterin...\n")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Kamera açılamadı!")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        recognized_frames = 0
        last_recognized = None
        confidence_history = []
        
        print("🎥 Yüz taranıyor... (Q ile çık)\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️  Kamera hatası! Lütfen Q'ya basarak çıkın...")
                cv2.waitKey(1)
                continue
            
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            best_match = None
            best_confidence = 0
            
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_region = gray[y:y+h, x:x+w]
                
                # Tüm kaydedilmiş yüzleri karşılaştır
                for name, face_data_list in db.items():
                    for face_data in face_data_list:
                        if isinstance(face_data, dict):
                            stored_face = face_data.get('frame', face_data)
                        else:
                            stored_face = face_data
                        
                        confidence = compare_faces(face_region, stored_face)
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = name
                
                confidence_history.append(best_confidence)
                if len(confidence_history) > 10:
                    confidence_history.pop(0)
                
                avg_confidence = np.mean(confidence_history) if confidence_history else 0
                
                # Sonuç göster
                if best_match and avg_confidence > 0.5:
                    recognized_frames += 1
                    last_recognized = best_match
                    color = (0, 255, 0)
                    result_text = f"✓ {best_match} | G: {avg_confidence:.2f}"
                else:
                    recognized_frames = 0
                    color = (0, 255, 255)
                    result_text = f"? Bilinmiyor | G: {best_confidence:.2f}"
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                cv2.putText(frame, result_text, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                if recognized_frames >= 3 and last_recognized:
                    print(f"\n✅ BAŞARILI! Hoşgeldiniz: {last_recognized}")
                    print(f"   Güven Skoru: {avg_confidence:.2f}")
                    cap.release()
                    cv2.destroyAllWindows()
                    return last_recognized
            
            cv2.putText(frame, "Q=Cik", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("YÜZ TANIMA - Hoşgeldiniz", frame)
            
            if cv2.waitKey(30) & 0xFF == ord('q'):
                print("\n❌ İşlem iptal edildi.\n")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("❌ Yüz tanınamadı.\n")
        
    except Exception as e:
        print(f"❌ Giriş sırasında hata: {e}\n")

def main_menu():
    """Ana menü"""
    while True:
        print("\n" + "="*70)
        print("🎯 YÜZ TANIMA SİSTEMİ - ANA MENÜ".center(70))
        print("="*70)
        print("\n1️⃣  Yüz Kaydet (Geliştirilmiş - Çoklu Açı)")
        print("2️⃣  Yüz ile Giriş (Geliştirilmiş)")
        print("3️⃣  Kayıtlı Kullanıcıları Listele")
        print("4️⃣  Veritabanını Temizle")
        print("5️⃣  Çık\n")
        
        choice = input("Seçim yazın (1-5): ").strip()
        
        if choice == '1':
            register_face_enhanced()
        elif choice == '2':
            login_face_enhanced()
        elif choice == '3':
            db = load_database()
            if db:
                print("\n📋 Kayıtlı Kullanıcılar:")
                for i, (name, data) in enumerate(db.items(), 1):
                    frame_count = len(data)
                    print(f"   {i}. {name} ({frame_count} kare)")
            else:
                print("\n❌ Veritabanı boş!")
        elif choice == '4':
            if os.path.exists(DB_PATH):
                response = input("\n⚠️  Tüm verileri silmek istediğinizden emin misiniz? (e/h): ").lower()
                if response == 'e':
                    os.remove(DB_PATH)
                    print("✓ Veritabanı silindi.")
            else:
                print("❌ Veritabanı zaten boş!")
        elif choice == '5':
            print("\n👋 Hoşça kalın!\n")
            break
        else:
            print("\n❌ Geçersiz seçim!")

if __name__ == "__main__":
    main_menu()
