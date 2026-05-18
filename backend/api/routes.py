from fastapi import APIRouter, HTTPException

from api.schemas import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    LivenessRequest, LivenessResponse, ModuleResultSchema,
    AuthenticateRequest, AuthenticateResponse,
    ChallengeRequest, ChallengeResponse,
    DiagnoseRequest, DiagnoseResponse,
    UserListResponse, DeleteResponse,
)
from core.recognition import extract_face_frames, recognize_from_frames
from core.liveness.manager import LivenessManager
from core.liveness.blink import BlinkModule
from core.liveness.eye_movement import EyeMovementModule
from core.liveness.head_movement import HeadMovementModule
from core.liveness.mouth_movement import MouthMovementModule
from core.decision_engine import decide
from core.diagnostics import analyze_frame
from db import store
from utils.image import decode_base64_image, to_rgb
from utils.constants import MIN_PASSED_CHECKS

router = APIRouter(prefix="/api")


def _build_manager() -> LivenessManager:
    return (
        LivenessManager()
        .add_module(BlinkModule())
        .add_module(EyeMovementModule())
        .add_module(HeadMovementModule())
        .add_module(MouthMovementModule())
    )


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/register", response_model=RegisterResponse)
def register(body: RegisterRequest):
    if store.user_exists(body.name):
        return RegisterResponse(success=False, message=f"'{body.name}' zaten kayıtlı")

    frames = [f for f in (decode_base64_image(b) for b in body.frames) if f is not None]
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

    user, _score, msg = recognize_from_frames(frames, db)
    if user:
        return LoginResponse(success=True, user=user, message=msg)
    return LoginResponse(success=False, message=msg)


@router.post("/liveness", response_model=LivenessResponse)
def liveness(body: LivenessRequest):
    if not body.frames:
        raise HTTPException(status_code=400, detail="Frame listesi boş")

    frames_rgb, timestamps = [], []
    for item in body.frames:
        bgr = decode_base64_image(item.get("frame", ""))
        if bgr is None:
            continue
        frames_rgb.append(to_rgb(bgr))
        timestamps.append(int(item.get("timestamp_ms", 0)))

    manager = _build_manager()
    results, error = manager.run(frames_rgb, timestamps)
    if error:
        return LivenessResponse(is_live=False, message=error, modules=[])

    passed_count = sum(1 for r in results if r.passed)
    is_live = passed_count >= MIN_PASSED_CHECKS
    msg = (
        "Canlı kişi tespit edildi"
        if is_live
        else f"Canlılık testi başarısız — eksik: {', '.join(r.module_name for r in results if not r.passed)}"
    )
    modules = [ModuleResultSchema(**r.__dict__) for r in results]
    return LivenessResponse(is_live=is_live, message=msg, modules=modules)


CHALLENGE_MODULES = {
    "blink":          BlinkModule,
    "eye_movement":   EyeMovementModule,
    "head_movement":  HeadMovementModule,
    "mouth_movement": MouthMovementModule,
}

CHALLENGE_MESSAGES = {
    "blink":          {"pass": "Göz kırpma tespit edildi",    "fail": "Yeterli göz kırpma algılanamadı"},
    "eye_movement":   {"pass": "Göz hareketi tespit edildi",  "fail": "Yeterli göz hareketi algılanamadı"},
    "head_movement":  {"pass": "Kafa hareketi tespit edildi", "fail": "Yeterli kafa hareketi algılanamadı"},
    "mouth_movement": {"pass": "Ağız hareketi tespit edildi", "fail": "Yeterli ağız hareketi algılanamadı"},
}


@router.post("/liveness/challenge", response_model=ChallengeResponse)
def liveness_challenge(body: ChallengeRequest):
    """Tek bir challenge'ı test eder (blink, eye_movement, head_movement, mouth_movement)."""
    if body.challenge not in CHALLENGE_MODULES:
        raise HTTPException(status_code=400, detail=f"Geçersiz challenge: {body.challenge}")
    if not body.frames:
        raise HTTPException(status_code=400, detail="Frame listesi boş")

    frames_rgb, timestamps = [], []
    for item in body.frames:
        bgr = decode_base64_image(item.get("frame", ""))
        if bgr is None:
            continue
        frames_rgb.append(to_rgb(bgr))
        timestamps.append(int(item.get("timestamp_ms", 0)))

    module = CHALLENGE_MODULES[body.challenge]()
    manager = LivenessManager().add_module(module)
    results, error = manager.run(frames_rgb, timestamps)

    if error or not results:
        return ChallengeResponse(challenge=body.challenge, passed=False, score=0.0, message=error or "Hata")

    r = results[0]
    msgs = CHALLENGE_MESSAGES[body.challenge]
    return ChallengeResponse(
        challenge=body.challenge,
        passed=r.passed,
        score=r.score,
        message=msgs["pass"] if r.passed else msgs["fail"],
        details=r.details,
    )


@router.post("/authenticate", response_model=AuthenticateResponse)
def authenticate(body: AuthenticateRequest):
    """
    Akış:
      1. username varsa → sadece o kullanıcıya karşı karşılaştır
      2. liveness_verified=True → challenge adımı zaten geçilmiş, liveness atla
      3. liveness_verified=False → tam liveness analizi çalıştır
      4. Yüz tanıma (face_recognition / dlib embedding)
      5. Decision engine → erişim kararı
    """
    db = store.load()
    if not db:
        return AuthenticateResponse(granted=False, reason="Kayıtlı kullanıcı yok")

    # username filtresi
    if body.username:
        db = {k: v for k, v in db.items() if k == body.username}
        if not db:
            return AuthenticateResponse(
                granted=False, reason=f"'{body.username}' kayıtlı değil"
            )

    bgr_frames = [f for f in (decode_base64_image(b) for b in body.frames) if f is not None]
    if not bgr_frames:
        return AuthenticateResponse(granted=False, reason="Geçerli frame alınamadı")

    # --- Liveness ---
    if body.liveness_verified:
        liveness_results = []
    else:
        rgb_frames = [to_rgb(f) for f in bgr_frames]
        timestamps = list(range(0, len(rgb_frames) * 100, 100))
        manager = _build_manager()
        liveness_results, error = manager.run(rgb_frames, timestamps)
        if error:
            return AuthenticateResponse(granted=False, reason=error)

    # --- Yüz tanıma ---
    user, rec_score, rec_msg = recognize_from_frames(bgr_frames, db)
    rec_result = {
        "user": user,
        "score": rec_score,
        "recognized": user is not None,
    }

    # --- Karar ---
    decision = decide(rec_result, liveness_results, liveness_pre_verified=body.liveness_verified)
    modules = [ModuleResultSchema(**r.__dict__) for r in liveness_results]

    return AuthenticateResponse(
        granted=decision["granted"],
        reason=decision["reason"],
        user=decision["details"].get("user"),
        recognition_score=decision["details"].get("recognition_score"),
        liveness=modules,
    )


@router.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(body: DiagnoseRequest):
    """
    Tek frame üzerinde tüm metrikleri döner.
    Test laboratuvarı için: EAR, MAR, head pose, landmark koordinatları.
    """
    bgr = decode_base64_image(body.frame)
    if bgr is None:
        return DiagnoseResponse(face_detected=False, error="Frame çözümlenemedi")
    rgb = to_rgb(bgr)
    result = analyze_frame(rgb)
    return DiagnoseResponse(**result)


@router.get("/users", response_model=UserListResponse)
def list_users():
    return UserListResponse(users=store.list_users())


@router.delete("/users/{name}", response_model=DeleteResponse)
def delete_user(name: str):
    ok, msg = store.delete_user(name)
    if not ok:
        raise HTTPException(status_code=404, detail=msg)
    return DeleteResponse(success=True, message=msg)
