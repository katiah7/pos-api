from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    username: str
    full_name: str
    role: str
    email: EmailStr | None = None

class UserCreate(UserBase):
    password_hash: str

class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None
    role: str | None = None
    email: EmailStr | None = None
    password_hash: str | None = None

class UserResponse(UserBase):
    user_id: int

    model_config = ConfigDict(
        from_attributes=True
    )