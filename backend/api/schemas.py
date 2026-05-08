from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    name: str
    # Base64 kodlu JPEG/PNG frame listesi (frontend kamerasından)
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
    # Birden fazla frame gönderilir; tanıma sliding window ile yapılır
    frames: list[str]


class LoginResponse(BaseModel):
    success: bool
    user: str | None = None
    message: str


class LivenessRequest(BaseModel):
    # Her eleman: {frame: base64_string, timestamp_ms: int}
    frames: list[dict]


class LivenessResponse(BaseModel):
    is_live: bool
    message: str


class UserListResponse(BaseModel):
    users: list[str]


class DeleteResponse(BaseModel):
    success: bool
    message: str
