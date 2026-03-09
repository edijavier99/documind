from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.core.security import hash_password, verify_password, create_token
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_user(data: UserRegister, db: Session) -> User:
    """
    Crea un nuevo usuario.
    Lanza error si el email ya existe.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("user registered", user_id=str(user.id), email=user.email)
    return user


def login_user(data: UserLogin, db: Session) -> TokenResponse:
    """
    Verifica credenciales y devuelve tokens.
    """
    user = db.query(User).filter(User.email == data.email).first()

    # Mismo error para email no encontrado y password incorrecto
    # (no revelar cuál de los dos falló)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    access_token = create_token(str(user.id), "access")
    refresh_token = create_token(str(user.id), "refresh")

    logger.info("user logged in", user_id=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


def refresh_access_token(refresh_token: str, db: Session) -> TokenResponse:
    """
    Dado un refresh token válido, genera un nuevo access token.
    """
    from jose import JWTError
    from app.core.security import decode_token

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = payload.get("sub")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return TokenResponse(
        access_token=create_token(str(user.id), "access"),
        refresh_token=create_token(str(user.id), "refresh"),
    )

