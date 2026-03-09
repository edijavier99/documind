from pydantic import BaseModel, EmailStr, field_validator
import re
from uuid import UUID


class UserRegister(BaseModel):
    """Lo que el cliente manda para registrarse"""
    email: EmailStr
    password: str
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    """Lo que el cliente manda para hacer login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Lo que el servidor devuelve tras login exitoso"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Para renovar el access token"""
    refresh_token: str


class UserResponse(BaseModel):
    """Info del usuario que devuelve la API (sin password)"""
    id: UUID
    email: str
    full_name: str | None
    is_active: bool

    model_config = {"from_attributes": True}  # permite crear desde modelo SQLAlchemy
