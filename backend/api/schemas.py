from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    name: str
    frames: list[str]

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("İsim boş olamaz")
        return v

    @field_validator("frames")
    @classmethod
    def frames_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("En az bir frame gerekli")
        return v


class RegisterResponse(BaseModel):
    success: bool
    message: str


class LoginRequest(BaseModel):
    frames: list[str]


class LoginResponse(BaseModel):
    success: bool
    user: str | None = None
    message: str


class ModuleResultSchema(BaseModel):
    module_name: str
    passed: bool
    score: float
    details: dict


class LivenessRequest(BaseModel):
    frames: list[dict]


class LivenessResponse(BaseModel):
    is_live: bool
    message: str
    modules: list[ModuleResultSchema] = []


class AuthenticateRequest(BaseModel):
    """Tek çağrıda liveness + tanıma + karar."""
    frames: list[str]
    username: str | None = None
    liveness_verified: bool = False


class AuthenticateResponse(BaseModel):
    granted: bool
    reason: str
    user: str | None = None
    recognition_score: float | None = None
    liveness: list[ModuleResultSchema] = []


class ChallengeRequest(BaseModel):
    """Tek bir liveness challenge testi."""
    challenge: str   # "blink" | "head_movement" | "eye_movement"
    frames: list[dict]  # [{frame: base64, timestamp_ms: int}]


class ChallengeResponse(BaseModel):
    challenge: str
    passed: bool
    score: float
    message: str
    details: dict = {}


class DiagnoseRequest(BaseModel):
    """Tek frame analizi — test laboratuvarı için."""
    frame: str  # base64


class DiagnoseResponse(BaseModel):
    face_detected: bool = False
    landmarks: list[list[float]] = []
    ear: float = 0.0
    mar: float = 0.0
    head_yaw: float = 0.0
    head_pitch: float = 0.0
    eye_dist: float = 0.0
    iris: dict = {}
    key_points: dict = {}
    thresholds: dict = {}
    error: str = ""


class UserListResponse(BaseModel):
    users: list[str]


class DeleteResponse(BaseModel):
    success: bool
    message: str
