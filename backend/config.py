import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', '')
    FIRESTORE_PROJECT_ID = os.getenv('FIRESTORE_PROJECT_ID', '')
    FACE_MATCH_THRESHOLD = float(os.getenv('FACE_MATCH_THRESHOLD', '0.50'))
    CHALLENGE_SUCCESS_RATIO = float(os.getenv('CHALLENGE_SUCCESS_RATIO', '0.80'))

settings = Settings()
