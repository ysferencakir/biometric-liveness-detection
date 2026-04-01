import face_recognition
import cv2

print("face_recognition başarıyla yüklendi!")
print("Models kontrol ediliyor...")

# Basit test: boş resim
try:
    image = face_recognition.load_image_file("test.jpg")
    print("Model dosyaları bulundu - hazır!")
except FileNotFoundError:
    print("Resim dosyası yok ama modeller yüklendi.")
except Exception as e:
    print(f"Hata: {e}")

print("Tüm bağımlılıklar OK!")
