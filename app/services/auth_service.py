from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from repositories.user_repository import user_repository


def authenticate(db: Session, username: str, password: str):
    user = user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )
    return {
        "access_token": create_access_token(user.user_id),
        "token_type": "bearer",
    }


def get_user_from_token(db: Session, token: str):
    """Validate a JWT and return its active database user."""
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise credential_error
        user_id = int(subject)
    except ValueError:
        raise credential_error
    if user_id <= 0:
        raise credential_error

    user = user_repository.get(db, user_id)
    if user is None:
        raise credential_error
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )
    return user
