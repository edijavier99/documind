from datetime import datetime, timedelta, timezone
from typing import Literal
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Contexto de hashing — bcrypt es el estándar para passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # bcrypt solo acepta hasta 72 bytes
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(plain_bytes, hashed_password)

def create_token(
    subject: str,  # normalmente el user_id
    token_type: Literal["access", "refresh"],
) -> str:
    """
    Genera un JWT firmado.

    El payload contiene:
    - sub: el user_id
    - type: access o refresh
    - exp: cuándo expira
    """
    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    payload = {
        "sub": str(subject),
        "type": token_type,
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # issued at
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza JWTError si el token es inválido o ha expirado.
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
