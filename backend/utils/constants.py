from pathlib import Path

# --- Kamera ---
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# --- Yüz Tespiti ---
HAAR_SCALE_FACTOR = 1.1
HAAR_MIN_NEIGHBORS = 4

# --- Yüz Tanıma ---
# Cosine similarity eşiği (0–1):
#   deepface/Facenet  → aynı kişi genellikle 0.50–0.70, öneri: 0.40
#   MediaPipe landmark → aynı kişi genellikle 0.90+,    öneri: 0.80
# .env dosyasında FACE_MATCH_THRESHOLD ile override edilebilir
FACE_MATCH_THRESHOLD = 0.40
# Giriş onayı için art arda kaç frame eşleşmeli
MIN_CONSECUTIVE_MATCHES = 3
# Kayan ortalama için güven geçmişi penceresi (frame sayısı)
CONFIDENCE_WINDOW = 10
# Kayıt için minimum yakalanması gereken frame sayısı
MIN_REGISTRATION_FRAMES = 15
# Giriş denemesi için maksimum süre (saniye)
LOGIN_MAX_DURATION = 30

# --- Canlılık Tespiti ---
# Göz en-boy oranı — bu değerin altındaysa göz kapalı sayılır
# 0.25 daha geniş tolerans sağlar (hızlı veya hafif kırpmalar da yakalanır)
EAR_THRESHOLD = 0.25
# Canlı kabul için minimum göz kırpma sayısı (1 kırpma yeterli)
MIN_BLINKS = 1
# Son 10 frame içinde ağız hareketi olması için minimum MAR değişimi
MAR_DELTA_THRESHOLD = 0.04
MAR_WINDOW = 10
# Kafa hareketini saymak için minimum açı değişimi (radyan)
HEAD_MOTION_THRESHOLD = 0.08
HEAD_MOTION_WINDOW = 15
# Karar vermeden önce geçmesi gereken minimum süre (saniye)
MIN_ELAPSED_BEFORE_DECISION = 3
# Canlı sayılmak için geçilmesi gereken minimum test adedi
# Aktif modül: blink + eye_movement + head_movement + mouth_movement = 4
# 2 geçerse canlı kabul et (kullanıcıya rastgele 2 challenge sorulduğu için)
MIN_PASSED_CHECKS = 2

# --- 3D Derinlik Kontrolü ---
# Sahte fotoğraf filtresi: göz mesafesi / yüz yüksekliği oranı
DEPTH_ASPECT_MIN = 0.3
DEPTH_ASPECT_MAX = 0.8
# Göz mesafesi / ağız mesafesi oranı
DEPTH_EYE_MOUTH_MIN = 1.5
DEPTH_EYE_MOUTH_MAX = 3.0

# --- MediaPipe Landmark İndeksleri (478 noktalı model) ---
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
MOUTH_INDICES = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375]
# İris landmark'ları (478-noktalı modelde 468-477 arası)
LEFT_IRIS_INDICES = [468, 469, 470, 471, 472]
RIGHT_IRIS_INDICES = [473, 474, 475, 476, 477]
# Göz hareketi için minimum piksel kayma eşiği
EYE_MOVEMENT_THRESHOLD = 8.0

# --- Dosya Yolları ---
_BACKEND_DIR = Path(__file__).resolve().parent.parent   # backend/
_PROJECT_ROOT = _BACKEND_DIR.parent                     # proje kökü
MODEL_PATH = str(_PROJECT_ROOT / "models" / "face_landmarker.task")
DB_PATH = str(_PROJECT_ROOT / "faces_db.pkl")
