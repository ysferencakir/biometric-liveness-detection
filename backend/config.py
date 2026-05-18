import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Uygulama
    SECRET_KEY: str = os.getenv("SECRET_KEY", "degistir-bunu-production-da")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS — virgülle ayrılmış origin listesi, örn: http://localhost:5173,http://localhost:3000
    # Development'ta * ile tüm origin'lere izin verilebilir
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # Firebase (opsiyonel — şimdilik pickle DB kullanılıyor)
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "")

    # Yüz tanıma eşikleri (.env ile override edilebilir)
    FACE_MATCH_THRESHOLD: float = float(os.getenv("FACE_MATCH_THRESHOLD", "0.50"))
    CHALLENGE_SUCCESS_RATIO: float = float(os.getenv("CHALLENGE_SUCCESS_RATIO", "0.80"))


settings = Settings()
