import os
import pickle

DB_PATH = "faces_db_enhanced.pkl"

def load_database():
    """Veritabanını yükle"""
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}


def save_database(db):
    """Veritabanını kaydet"""
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)


def get_registered_users():
    """Kayıtlı kullanıcıların listesini al"""
    db = load_database()
    return list(db.keys())


def delete_user(name):
    """Kullanıcıyı veritabanından sil"""
    try:
        db = load_database()
        if name in db:
            del db[name]
            save_database(db)
            return True, f"{name} silindi"
        return False, "Kullanıcı bulunamadı"
    except Exception as e:
        return False, f"Hata: {str(e)}"
