from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshRequest,
    UserResponse,
)
from app.models.user import User
from app.services.auth_services import register_user, login_user, refresh_access_token
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Crea una cuenta nueva.

    - Valida que el email no esté en uso
    - Hashea el password
    - Devuelve el usuario creado (sin password)
    """
    user = register_user(data, db)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Login con email y password.
    Devuelve access_token y refresh_token.
    """
    return login_user(data, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """
    Renueva el access token usando el refresh token.
    Llama a este endpoint cuando el access token expire.
    """
    return refresh_access_token(data.refresh_token, db)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Devuelve el usuario autenticado actual.
    Requiere Authorization: Bearer <token>
    """
    return current_user
