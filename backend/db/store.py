import os
import pickle
from utils.constants import DB_PATH


def load() -> dict:
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}


def save(db: dict) -> None:
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)


def list_users() -> list[str]:
    return list(load().keys())


def add_user(name: str, face_data: list[dict]) -> tuple[bool, str]:
    db = load()
    if name in db:
        return False, f"'{name}' zaten kayıtlı"
    db[name] = face_data
    save(db)
    return True, f"{name} kaydedildi ({len(face_data)} kare)"


def delete_user(name: str) -> tuple[bool, str]:
    db = load()
    if name not in db:
        return False, "Kullanıcı bulunamadı"
    del db[name]
    save(db)
    return True, f"{name} silindi"


def user_exists(name: str) -> bool:
    return name in load()
