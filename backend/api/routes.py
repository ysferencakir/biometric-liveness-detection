from fastapi import APIRouter, HTTPException
from api.schemas import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    LivenessRequest, LivenessResponse,
    UserListResponse, DeleteResponse,
)
from core.recognition import extract_face_frames, recognize_from_frames
from core.liveness import analyze_liveness
from db import store
from utils.image import decode_base64_image, to_rgb

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/register", response_model=RegisterResponse)
def register(body: RegisterRequest):
    if store.user_exists(body.name):
        return RegisterResponse(success=False, message=f"'{body.name}' zaten kayıtlı")

    frames = [decode_base64_image(f) for f in body.frames]
    face_data, error = extract_face_frames(frames)

    if error:
        return RegisterResponse(success=False, message=error)

    ok, msg = store.add_user(body.name, face_data)
    return RegisterResponse(success=ok, message=msg)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    db = store.load()
    if not db:
        return LoginResponse(success=False, message="Veritabanında kayıtlı kullanıcı yok")
    frames = [f for f in (decode_base64_image(b) for b in body.frames) if f is not None]
    if not frames:
        return LoginResponse(success=False, message="Geçerli frame alınamadı")
    user, msg = recognize_from_frames(frames, db)

    if user:
        return LoginResponse(success=True, user=user, message=msg)
    return LoginResponse(success=False, message=msg)


@router.post("/liveness", response_model=LivenessResponse)
def liveness(body: LivenessRequest):
    if not body.frames:
        raise HTTPException(status_code=400, detail="Frame listesi boş")

    frames_rgb = []
    timestamps = []

    for item in body.frames:
        frame_b64 = item.get("frame", "")
        ts = int(item.get("timestamp_ms", 0))
        bgr = decode_base64_image(frame_b64)
        if bgr is None:
            continue
        frames_rgb.append(to_rgb(bgr))
        timestamps.append(ts)

    is_live, msg = analyze_liveness(frames_rgb, timestamps)
    return LivenessResponse(is_live=is_live, message=msg)


@router.get("/users", response_model=UserListResponse)
def list_users():
    return UserListResponse(users=store.list_users())


@router.delete("/users/{name}", response_model=DeleteResponse)
def delete_user(name: str):
    ok, msg = store.delete_user(name)
    if not ok:
        raise HTTPException(status_code=404, detail=msg)
    return DeleteResponse(success=True, message=msg)
