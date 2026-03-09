import pytest
from app.core.security import hash_password, verify_password, create_token, decode_token


def test_password_hashing():
    password = "MyPassword123"
    hashed = hash_password(password)

    # El hash es diferente al original
    assert hashed != password

    # Pero verifica correctamente
    assert verify_password(password, hashed) is True

    # Un password incorrecto no verifica
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_access_token():
    token = create_token("user-123", "access")
    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    token = create_token("user-123", "refresh")
    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"
