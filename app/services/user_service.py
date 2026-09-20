from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import hash_password
from repositories.user_repository import user_repository
from schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int):
    user = user_repository.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def list_user(db: Session):
    return user_repository.get_all(db)


def create_user(db: Session, data: UserCreate):
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    values = data.model_dump(exclude={"password"})
    values["password_hash"] = hash_password(data.password)
    return user_repository.create(db, values)


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user(db, user_id)
    values = data.model_dump(exclude_unset=True)
    password = values.pop("password", None)
    if password is not None:
        values["password_hash"] = hash_password(password)
    return user_repository.update(db, user, values)


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    user_repository.delete(db, user)
