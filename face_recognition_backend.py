from face_registration import register_face_web
from face_login import login_face_web
from face_db import get_registered_users, delete_user, load_database, save_database
from face_liveness import check_liveness

# Eski arayüz için geriye dönük uyumluluk
DB_PATH = 'faces_db_enhanced.pkl'
